from datetime import datetime
from django.db.models import F, Count, Q, Max

from django.utils import timezone

from django.shortcuts import render, redirect

from django.contrib.auth.decorators import login_required

from apps.attendance import models
from apps.attendance.models import Attendance
from apps.courses.models import Department, DepartmentLevel
from apps.home.utils import send_custom_message
from apps.subjects.models import Subject

from django.utils.timezone import now, timedelta

from apps.users.models import StudentArchiveHistory, StudentProfile


def is_admin(user):
    return user.is_admin


@login_required
def index(request):
    today = timezone.now().date()
    month_start = today.replace(day=1)

    # 1. Absents aujourd'hui
    absents_aujourdhui = Attendance.objects.filter(date=today, status="absent").count()

    # 2. Absents ce mois
    absents_mois = Attendance.objects.filter(
        date__gte=month_start, date__lte=today, status="absent"
    ).count()

    # 3. Alertes critiques (exemple : nombre de profils archivés vs en cours)
    total_archives = StudentProfile.objects.filter(archived=True).count()

    en_cours = StudentProfile.objects.filter(archived=False).count()

    # 4. Absents récents (ex: les 5 derniers)
    absents_recents = Attendance.objects.filter(status="absent").order_by("-date")[:5]

    # 5. Archives récentes (ex: derniers archivages)
    archives_recentes = StudentArchiveHistory.objects.select_related(
        "student__user"
    ).order_by("-performed_at")[
        :5
    ]  # si tu as ce modèle

    # 6. Absences par filière
    absences_par_filiere = DepartmentLevel.objects.annotate(
        absences=Count(
            "students__attendances", filter=Q(students__attendances__status="absent")
        ),
        archives=Count("students", filter=Q(students__archived=True)),
        total=Count("students"),
    ).values("id", "level__name", "department__name", "absences", "archives", "total")

    absences_par_filiere_data = []
    for f in absences_par_filiere:
        pourcentage = (
            round((f["absences"] / f["total"]) * 100, 2) if f["total"] > 0 else 0
        )
        absences_par_filiere_data.append(
            {
                "nom": f"{f['department__name']} - {f['level__name']}",
                "absences": f["absences"],
                "pourcentage": pourcentage,
                "archives": f["archives"],
            }
        )

    # 7. Absences par matière
    absences_par_matiere = Subject.objects.annotate(
        absences=Count("attendance", filter=Q(attendance__status="absent")),
        total=Count("attendance"),
    ).values("name", "absences", "total")

    absences_par_matiere_data = []
    for m in absences_par_matiere:
        pourcentage = (
            round((m["absences"] / m["total"]) * 100, 2) if m["total"] > 0 else 0
        )
        absences_par_matiere_data.append(
            {
                "nom": m["name"],
                "absences": m["absences"],
                "pourcentage": pourcentage,
            }
        )

    context = {
        "segment": "index",
        "absents_aujourdhui": absents_aujourdhui,
        "absents_mois": absents_mois,
        "alertes_archives": total_archives,
        "alertes_cours": en_cours,
        "absents_recents": absents_recents,
        "archives_recent": archives_recentes,
        "absences_par_filiere": absences_par_filiere_data,
        "absences_par_matiere": absences_par_matiere_data,
    }

    return render(request, "home/index.html", context)


@login_required
def statistiques_view(request):
    vue = request.GET.get("vue", "filiere")
    periode = request.GET.get("periode", "mois")

    # Filtrage par période
    today = now().date()
    if periode == "semaine":
        start_date = today - timedelta(days=7)
    elif periode == "mois":
        start_date = today.replace(day=1)
    elif periode == "annee":
        start_date = today.replace(month=1, day=1)
    else:
        start_date = None

    attendances = Attendance.objects.filter(status="absent")
    if start_date:
        attendances = attendances.filter(date__date__gte=start_date)

    headers, rows = [], []

    # Vue par filière
    if vue == "filiere":
        headers = ["Filière", "Absences", "Pourcentage", "Archivés"]
        data = attendances.values(
            filiere=F("student__major__department__name"),
            niveau=F("student__major__level__name"),
        ).annotate(
            total_abs=Count("id"), total_etudiants=Count("student", distinct=True)
        )

        for item in data:
            filiere_label = f"{item['filiere']} - {item['niveau']}"
            total_students = StudentProfile.objects.filter(
                major__department__name=item["filiere"],
                major__level__name=item["niveau"],
            ).count()
            archives = StudentProfile.objects.filter(
                major__department__name=item["filiere"],
                major__level__name=item["niveau"],
                archived=True,
            ).count()

            pourcentage = f"{round((item['total_abs'] / total_students) * 100, 1) if total_students else 0}%"
            rows.append([filiere_label, item["total_abs"], pourcentage, archives])

    # Vue par matière
    elif vue == "matiere":
        headers = ["Matière", "Absences", "Pourcentage"]
        data = attendances.values(nom_matiere=F("subject__name")).annotate(
            total_abs=Count("id")
        )
        total_absences = attendances.count()
        for item in data:
            pourcentage = f"{round((item['total_abs'] / total_absences) * 100, 1) if total_absences else 0}%"
            rows.append([item["nom_matiere"], item["total_abs"], pourcentage])

    # Vue matière + filière
    elif vue == "matiere_filiere":
        headers = ["Filière", "Matière", "Absences"]
        data = attendances.values(
            filiere=F("student__major__department__name"), matiere=F("subject__name")
        ).annotate(total_abs=Count("id"))
        for item in data:
            rows.append([item["filiere"], item["matiere"], item["total_abs"]])

    context = {
        "tableau": {
            "headers": headers,
            "rows": rows,
        }
    }
    return render(request, "home/statistiques.html", context)


@login_required
def liste_presence_view(request):
    filiere = request.GET.get("filiere", "toutes")
    statut = request.GET.get("statut", "tous").lower()
    date_str = request.GET.get("date")  # format attendu 'YYYY-MM-DD'

    # Parse la date ou utilise aujourd'hui
    try:
        filter_date = (
            datetime.strptime(date_str, "%Y-%m-%d").date()
            if date_str
            else timezone.localdate()
        )
    except ValueError:
        filter_date = timezone.localdate()

    # Liste des filières (DepartmentLevel) ordonnée alphabétiquement sur le label
    filieres_disponibles = (
        DepartmentLevel.objects.select_related("department", "level")
        .order_by("level__name", "department__name")
        .values_list("id", "level__name", "department__name")
        .distinct()
    )
    filieres_disponibles = [
        {"id": f[0], "label": f"{f[1]} - {f[2]}"} for f in filieres_disponibles
    ]

    # Statuts
    statuts_disponibles = ["present", "absent", "justified", "archive"]

    # Filtrage des présences uniquement sur la date donnée
    attendances_qs = Attendance.objects.select_related(
        "student__user",
        "student__major__department",
        "student__major__level",
    ).filter(
        date__date=filter_date  # filtrage sur la date seulement
    )

    # Filtrage filière (DepartmentLevel.id)
    if filiere != "toutes":
        try:
            filiere_id = int(filiere)
            attendances_qs = attendances_qs.filter(student__major_id=filiere_id)
        except ValueError:
            pass

    # Filtrage statut
    if statut != "tous":
        if statut == "archive":
            attendances_qs = attendances_qs.filter(student__archived=True)
        else:
            attendances_qs = attendances_qs.filter(status=statut)

    # Pour éviter doublons (plusieurs matières), on prend la présence la plus récente par étudiant
    # Ici on récupère les ids max (le plus récent) par étudiant pour la date donnée
    latest_ids = (
        attendances_qs.values("student_id")
        .annotate(latest_id=Max("id"))
        .values_list("latest_id", flat=True)
    )

    attendances = (
        Attendance.objects.filter(id__in=latest_ids)
        .select_related(
            "student__user",
            "student__major__department",
            "student__major__level",
        )
        .order_by("student__user__last_name", "student__user__first_name")
    )

    # Préparation pour le template
    liste_etudiants = []
    for att in attendances:
        liste_etudiants.append(
            {
                "id": att.student.user.pk,
                "nom": att.student.user.get_full_name(),
                "filiere": (
                    f"{att.student.major.level.name} - {att.student.major.department.name}"
                    if att.student.major
                    else "Non assigné"
                ),
                "statut": (
                    "Archivé"
                    if att.student.archived
                    else dict(Attendance.STATUS_CHOICES).get(att.status, "Inconnu")
                ),
            }
        )
    context = {
        "liste_etudiants": liste_etudiants,
        "filieres_disponibles": filieres_disponibles,
        "statuts_disponibles": statuts_disponibles,
        "filiere_active": filiere,
        "statut_actif": statut,
        "date_active": filter_date.strftime("%Y-%m-%d"),
    }
    return render(
        request,
        "home/presence.html",
        context,
    )


@login_required
def archives_view(request):
    # Récupération des paramètres GET
    filiere_id = request.GET.get("filiere", "toutes")
    date_archivage = request.GET.get("date", "")

    # Base queryset
    archived_students = StudentProfile.objects.filter(archived=True)

    # Filtre par filière
    if filiere_id != "toutes":
        archived_students = archived_students.filter(major_id=filiere_id)

    # Filtre par date d’archivage (optionnel)
    if date_archivage:
        try:
            date_obj = datetime.strptime(date_archivage, "%Y-%m-%d").date()
            archived_students = archived_students.filter(archived_at__date=date_obj)
        except ValueError:
            pass  # Ignore si format invalide

    # Annoter avec le nombre d’absences (présences != "present")
    archived_students = archived_students.annotate(
        nb_absences=Count("attendances", filter=~Q(attendances__status="present"))
    ).select_related("major__department", "major__level")

    # Récupérer toutes les filières existantes pour le filtre, triées par nom
    filieres = DepartmentLevel.objects.order_by("department__name").select_related(
        "department", "level"
    )

    return render(
        request,
        "home/archives.html",
        {
            "liste_archives": archived_students,
            "filieres": filieres,
            "filiere_active": filiere_id,
            "date_active": date_archivage,
        },
    )


@login_required
def import_data_view(request):
    if request.method == "POST":
        data_type = request.POST.get("data_type")
        excel_file = request.FILES.get("excel_file")

        if not excel_file:
            send_custom_message(
                (request, "Veuillez sélectionner un fichier Excel."), "error"
            )
            return redirect("import-page")

        # TODO: traitement du fichier Excel selon `data_type`
        send_custom_message(
            (request, f"Importation de {data_type} en cours..."), "success"
        )
        return redirect("import-page")

    return render(request, "home/import_page.html")


@login_required
def redirect_after_login(request):
    user = request.user
    if user.role == "teacher":
        return redirect("teacher:dashboard")
    else:
        return redirect("home:index")
