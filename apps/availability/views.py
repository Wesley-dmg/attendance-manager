from django.db.models import Prefetch
from django.urls import reverse_lazy
from django.views.generic import ListView, UpdateView,DeleteView,RedirectView
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View

from django.http import JsonResponse
from apps.availability.forms import AvailabilityRequestForm
from apps.availability.models import AvailabilityRequest, AvailabilityResponse
from apps.availability.utils import send_availability_request_notification, validate_teacher_ids
from apps.common.models import DepartmentLevelSubject
from apps.home.utils import send_custom_message
from apps.subjects.models import Subject

from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import user_passes_test,login_required

from apps.users.models import TeacherProfile

from django.db import transaction

from django.utils.translation import gettext_lazy as _

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

class AvailabilityRequestListView(ListView):
    model = AvailabilityRequest
    template_name = 'availability/admin/availability_request_list.html'
    context_object_name = 'requests'

    def get_queryset(self):
        # Précharger les réponses pour chaque demande via prefetch_related
        responses = AvailabilityResponse.objects.all()
        return AvailabilityRequest.objects.prefetch_related(Prefetch('responses', queryset=responses)).all()

@method_decorator([login_required, user_passes_test(lambda u: u.is_admin)], name='dispatch')
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

# Fonction principale pour créer une demande de disponibilité
@transaction.atomic
def create_availability_request(request):
    if request.method != "POST":
        send_custom_message(request, _("Méthode non autorisée"), 'error')
        return redirect('availability:create_request')

    try:
        # Récupérer les données envoyées depuis le frontend
        subject_id = request.POST.get("subject_id")
        teacher_ids = request.POST.get("teacher_ids", "").split(",")
        filiere_ids = request.POST.get("filiere_ids", "").split(",")
        days = request.POST.getlist("days")

        # Validation des données
        if not subject_id or not teacher_ids or not days:
            send_custom_message(request, _("Données incomplètes. Veuillez vérifier les informations envoyées."), 'error')
            return redirect('availability:create_request')  # Rediriger immédiatement après l'erreur

        teacher_ids = validate_teacher_ids(teacher_ids)
        if not teacher_ids:
            send_custom_message(request, _("IDs enseignants invalides. Vérifiez les identifiants des enseignants."), 'error')
            return redirect('availability:create_request')  # Rediriger immédiatement après l'erreur

        # Récupérer la matière associée
        subject = get_object_or_404(Subject, id=subject_id)

        # Récupérer les enseignants associés
        teachers = TeacherProfile.objects.filter(id__in=teacher_ids)
        if not teachers.exists():
            send_custom_message(request, _("Aucun enseignant valide trouvé. Vérifiez les IDs."), 'error')
            return redirect('availability:create_request')  # Rediriger immédiatement après l'erreur

        # Créer la demande de disponibilité
        availability_request = AvailabilityRequest.objects.create(
            subject=subject,
            days=days
        )

        # Associer les enseignants à la demande
        availability_request.teachers.set(teachers)

        # Créer une réponse en attente pour chaque enseignant
        responses = [
            AvailabilityResponse(
                request=availability_request,
                teacher=teacher,
                status='pending'
            ) for teacher in teachers
        ]
        AvailabilityResponse.objects.bulk_create(responses)

        # Message de succès avec redirection vers une autre page
        send_custom_message(request, _("Demande de disponibilité créée avec succès !"), 'success')
        
        # # Envoi du message de notification aux enseignants
        # send_availability_request_notification(teachers, subject, filieres, days)
        return redirect('availability:availability_request_list')

    except Exception as e:
        send_custom_message(request, _("Erreur interne : {0}".format(str(e))), 'error')
        return redirect('availability:create_request')  # Redirige en cas d'erreur interne


class AvailabilityRequestUpdateView(UpdateView):
    model = AvailabilityRequest
    fields = ['subject', 'teachers', 'days']
    template_name = 'availability_request_form.html'
    success_url = reverse_lazy('availability_request_list')
    
class AvailabilityRequestDeleteView(DeleteView):
    model = AvailabilityRequest
    template_name = 'availability/admin/confirm_delete.html'
    context_object_name = 'availability_request'
    success_url = reverse_lazy('availability:availability_request_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['cancel_url'] = reverse_lazy('availability:availability_request_list')
        # Utilise self.request.user pour récupérer l'utilisateur connecté
        context['user'] = self.request.user
        return context

    def delete(self, request, *args, **kwargs):
        send_custom_message(self.request, _("Demande de disponibilité supprimée avec succès."), 'success')
        return super().delete(request, *args, **kwargs)

# class TeacherAvailabilityRequestListView(ListView):
#     model = AvailabilityRequest
#     template_name = 'availability/teacher/availability_request_list.html'  # Le template à créer
#     context_object_name = 'requests'

#     def get_queryset(self):
#         # Filtrer les demandes de disponibilité pour le professeur connecté
#         teacher = self.request.user.teacherprofile
#         status_filter = self.request.GET.get('status')  # Récupérer le filtre de statut depuis la requête

#         # Filtrer selon le statut de la réponse
#         if status_filter == 'approved':
#             return AvailabilityRequest.objects.filter(responses__teacher=teacher, responses__status='accepted')
#         elif status_filter == 'rejected':
#             return AvailabilityRequest.objects.filter(responses__teacher=teacher, responses__status='rejected')
#         else:
#             return AvailabilityRequest.objects.filter(responses__teacher=teacher)  # Toutes les demandes

class TeacherAvailabilityRequestListView(ListView):
    model = AvailabilityRequest
    template_name = 'availability/teacher/availability_request_list.html'  # Le template à créer
    context_object_name = 'requests'

    def get_queryset(self):
        # Filtrer les demandes de disponibilité pour le professeur connecté
        teacher = self.request.user.teacherprofile

        # Récupérer le paramètre de filtre 'status' depuis l'URL (GET)
        status_filter = self.request.GET.get('status')  # Par exemple, 'all', 'approved', 'rejected', 'pending'

        # Par défaut, afficher toutes les demandes de disponibilité
        queryset = AvailabilityRequest.objects.filter(responses__teacher=teacher)

        # Appliquer le filtre si un statut est spécifié
        if status_filter:
            if status_filter == 'approved':
                queryset = queryset.filter(responses__status='accepted')
            elif status_filter == 'rejected':
                queryset = queryset.filter(responses__status='rejected')
            elif status_filter == 'pending':
                queryset = queryset.filter(responses__status='pending')

        return queryset

    def get_context_data(self, **kwargs):
        # Ajouter les filtres disponibles dans le contexte pour affichage
        context = super().get_context_data(**kwargs)
        context['status_filter'] = self.request.GET.get('status', '')  # Le filtre actuel (ex: 'approved', 'rejected', 'pending')
        return context
    
class TeacherAvailabilityPendingRequestView(ListView):
    model = AvailabilityRequest
    template_name = 'availability/teacher/availability_pending_request_list.html'
    context_object_name = 'requests'

    def get_queryset(self):
        teacher = self.request.user.teacherprofile
        return AvailabilityRequest.objects.filter(responses__teacher=teacher, responses__status='pending')

def accept_availability_request(request, request_id):
    availability_request = get_object_or_404(AvailabilityRequest, pk=request_id)
    response = get_object_or_404(AvailabilityResponse, request=availability_request, teacher=request.user.teacherprofile)

    # Mettre à jour le statut de la réponse à "accepté"
    response.status = 'accepted'
    response.save()

    # Message de succès
    send_custom_message(request, _("Demande acceptée avec succès."), 'success')
    
    return redirect('availability:teacher_availability_pending_request_list')  # Redirection vers la liste des demandes en attente

def reject_availability_request(request, request_id):
    availability_request = get_object_or_404(AvailabilityRequest, pk=request_id)
    response = get_object_or_404(AvailabilityResponse, request=availability_request, teacher=request.user.teacherprofile)

    # Mettre à jour le statut de la réponse à "rejeté"
    response.status = 'rejected'
    response.save()

    # Message de succès
    send_custom_message(request, _("Demande rejetée avec succès."), 'error')

    return redirect('availability:teacher_availability_pending_request_list')  # Redirection vers la liste des demandes en attente

# class AvailabilityRequestAcceptRejectView(RedirectView):
#     # On utilise RedirectView car après l'action (acceptation/rejet), on redirige vers une autre page
#     def get_redirect_url(self, *args, **kwargs):
#         request = get_object_or_404(AvailabilityRequest, pk=kwargs['pk'])
#         action = kwargs['action']  # 'accept' ou 'reject'

#         if action == 'accept':
#             request.status = 'accepted'
#         elif action == 'reject':
#             request.status = 'rejected'
        
#         request.save()

#         # Rediriger vers la page de liste des demandes
#         return reverse_lazy('availability:teacher_availability_request_list')
