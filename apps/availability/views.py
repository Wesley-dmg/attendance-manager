from django.shortcuts import get_object_or_404, redirect, render
from django.views import View

from django.http import JsonResponse

from apps.availability.forms import AvailabilityRequestForm
from apps.availability.models import AvailabilityRequest, AvailabilityResponse
from apps.common.models import DepartmentLevelSubject
from apps.subjects.models import Subject

from apps.users.models import TeacherProfile

from django.views.decorators.csrf import csrf_exempt
from django.db import transaction
import json

def get_teachers_for_subject(request):
    # Vérifie si la requête est une requête AJAX
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest' and 'subject_id' in request.GET:
        try:
            subject_id = int(request.GET['subject_id'])
        except ValueError:
            return JsonResponse({'error': 'Invalid subject ID'}, status=400)

        # Récupère la matière avec cet ID
        subject = get_object_or_404(Subject, id=subject_id)

        # Récupère les enseignants associés à cette matière via la relation ManyToMany
        teachers = TeacherProfile.objects.filter(subjects=subject)

        # Prépare les données des enseignants pour la réponse JSON
        data = {
            'teachers': [{'id': t.id, 'name': t.user.get_full_name()} for t in teachers],
        }
        return JsonResponse(data)

    return JsonResponse({'error': 'Invalid request'}, status=400)

def get_filieres(request):
    """
    Retourne les filières associées à une matière donnée.
    """
    if request.method == "GET" and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        subject_id = request.GET.get("subject_id")
        
        if not subject_id:
            return JsonResponse({"error": "Aucun ID de matière fourni."}, status=400)

        # Debug : Vérification de l'ID de matière
        print(f"ID de matière reçu : {subject_id}")

        # Récupérer la matière avec l'ID fourni
        subject = get_object_or_404(Subject, id=subject_id)

        # Debug : Affichage de la matière trouvée
        print(f"Matière trouvée : {subject.name} (ID: {subject.id})")

        # Récupérer les relations DepartmentLevelSubject associées à cette matière
        dept_level_subjects = DepartmentLevelSubject.objects.filter(subject=subject)

        # Debug : Nombre de relations trouvées
        print(f"Nombre de relations trouvées pour la matière : {dept_level_subjects.count()}")

        # Préparer la liste des filières à renvoyer
        filiere_list = [
            {
                "id": dept_level.department_level.id,  # ID de la filière (niveau départemental)
                "name": dept_level.get_full_description()  # Description complète de la filière
            }
            for dept_level in dept_level_subjects
        ]

        # Debug : Afficher les filières récupérées
        print(f"Filières associées : {filiere_list}")

        # Retourner les filières en réponse JSON
        return JsonResponse({"filieres": filiere_list}, status=200)

    return JsonResponse({"error": "Requête invalide."}, status=400)

class CreateAvailabilityRequestView(View):
    """
    Vue pour afficher le formulaire de création d'une demande et gérer la soumission.
    """
    template_name = "availability/admin/create_request.html"

    def get(self, request):
        """
        Gère l'affichage du template avec les matières et le formulaire des jours.
        """
        subjects = Subject.objects.all()
        availability_form = AvailabilityRequestForm()  
        context={
            'subjects': subjects,
            'availability_form': availability_form,
        }
        return render(request, self.template_name, context)

@csrf_exempt
@transaction.atomic
def create_availability_request(request):
    if request.method == "POST":
        try:
            # Récupérer les données envoyées depuis le frontend
            subject_id = request.POST.get("subject_id")
            teacher_ids = request.POST.get("teacher_ids", "").split(",")
            filiere_ids = request.POST.get("filiere_ids", "").split(",")  # Si nécessaire plus tard
            days = request.POST.getlist("days")

            # Valider les données reçues
            if not subject_id or not teacher_ids or not days:
                return JsonResponse({"error": "Données incomplètes"}, status=400)

            # Récupérer la matière associée
            subject = get_object_or_404(Subject, id=subject_id)

            # Récupérer les enseignants associés
            teachers = TeacherProfile.objects.filter(id__in=teacher_ids)
            if not teachers.exists():
                return JsonResponse({"error": "Aucun enseignant valide trouvé"}, status=400)

            # Créer la demande de disponibilité
            availability_request = AvailabilityRequest.objects.create(
                subject=subject,
                days=days
            )

            # Associer les enseignants à la demande
            availability_request.teachers.set(teachers)

            # Créer une réponse en attente pour chaque enseignant
            AvailabilityResponse.objects.bulk_create([
                AvailabilityResponse(
                    request=availability_request,
                    teacher=teacher,
                    status='pending'
                ) for teacher in teachers
            ])

            # Répondre avec un message de succès
            return JsonResponse({"message": "Demande de disponibilité créée avec succès"}, status=201)

        except Exception as e:
            # En cas d'erreur, annuler la transaction et renvoyer une erreur
            return JsonResponse({"error": str(e)}, status=500)
    else:
        return JsonResponse({"error": "Méthode non autorisée"}, status=405)
