# from django.contrib import messages
from django.shortcuts import render, redirect

# from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required

from apps.home.utils import send_custom_message

# from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin

from .models import *


def is_admin(user):
    return user.is_admin


@login_required
def index(request):

    context = {
        "segment": "index",
        "absences_par_filiere": [
            {"nom": "Informatique", "absences": 20, "pourcentage": 40, "archives": 3},
            {"nom": "Maths", "absences": 10, "pourcentage": 20, "archives": 1},
        ],
        "absences_par_matiere": [
            {"nom": "Algèbre", "absences": 15, "pourcentage": 35},
            {"nom": "Programmation", "absences": 5, "pourcentage": 10},
        ],
    }
    return render(request, "home/index.html", context)


@login_required
def statistiques_view(request):
    vue = request.GET.get("vue", "filiere")
    periode = request.GET.get("periode", "mois")

    # Exemple de simulation de données (à remplacer avec des requêtes réelles)
    headers, rows = [], []

    if vue == "filiere":
        headers = ["Filière", "Absences", "Pourcentage", "Archivés"]
        rows = [
            ["SIL - L1", 20, "35%", 3],
            ["SIL - L2", 10, "55%", 1],
            ["RIT - L2", 2, "5%", 1],
        ]
    elif vue == "matiere":
        headers = ["Matière", "Absences", "Pourcentage"]
        rows = [
            ["Analyse des données", 15, "30%"],
            ["Algèbre linéaire ", 5, "10%"],
        ]
    elif vue == "matiere_filiere":
        headers = ["Filière", "Matière", "Absences"]
        rows = [
            ["Informatique", "POO", 8],
            ["Maths", "Statistiques", 4],
        ]

    context = {
        "tableau": {
            "headers": headers,
            "rows": rows,
        },
    }
    return render(request, "home/statistiques.html", context)


@login_required
def liste_presence_view(request):
    filiere = request.GET.get("filiere", "toutes")
    statut = request.GET.get("statut", "tous")

    # Fausse base de données simulée
    all_students = [
        {"id": 1, "nom": "Ali K.", "filiere": "Informatique", "statut": "Absent"},
        {"id": 2, "nom": "Sarah M.", "filiere": "Mathématiques", "statut": "Présent"},
        {"id": 3, "nom": "Lina G.", "filiere": "Physique", "statut": "Archivé"},
        {"id": 4, "nom": "David L.", "filiere": "Informatique", "statut": "Présent"},
        {"id": 5, "nom": "Aminata B.", "filiere": "Mathématiques", "statut": "Absent"},
    ]

    # Filtrage
    filtered = all_students
    if filiere != "toutes":
        filtered = [etu for etu in filtered if etu["filiere"].lower() == filiere]
    if statut != "tous":
        filtered = [etu for etu in filtered if etu["statut"].lower() == statut]

    return render(request, "home/presence.html", {"liste_etudiants": filtered})


@login_required
def archives_view(request):
    filiere = request.GET.get("filiere", "toutes")

    # Simuler des données archivées
    archived_students = [
        {"nom": "Ali", "prenom": "Karim", "filiere": "Informatique", "nb_absences": 8},
        {
            "nom": "Sarah",
            "prenom": "Mehdi",
            "filiere": "Mathématiques",
            "nb_absences": 5,
        },
        {"nom": "Lina", "prenom": "Giraud", "filiere": "Physique", "nb_absences": 12},
        {
            "nom": "Yann",
            "prenom": "Dupont",
            "filiere": "Informatique",
            "nb_absences": 3,
        },
    ]

    filtered = archived_students
    if filiere != "toutes":
        filtered = [
            etu for etu in archived_students if etu["filiere"].lower() == filiere
        ]

    return render(request, "home/archives.html", {"liste_archives": filtered})


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
