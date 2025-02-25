from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import user_passes_test,login_required
from django.db.models import Prefetch
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _

from django.views.generic import ListView, UpdateView,DeleteView
from django.views import View

from django.shortcuts import get_object_or_404, redirect, render

from apps.common.models import DepartmentLevelSubject
from apps.subjects.models import Subject
from apps.availability.models import AvailabilityRequest, AvailabilityResponse
from apps.users.models import TeacherProfile

from apps.home.utils import send_custom_message
from apps.availability.utils import validate_teacher_ids

from django.db import transaction

from django.urls import reverse
from django.utils.timesince import timesince

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
    try:
        if request.method == "GET":
            subject_id = request.GET.get("subject_id")
            if not subject_id:
                return JsonResponse({"error": "Aucun ID de matière fourni."}, status=400)
            
            subject = get_object_or_404(Subject, id=subject_id)
            dept_level_subjects = DepartmentLevelSubject.objects.filter(subject=subject)

            filiere_list = []
            for dls in dept_level_subjects:
                dep_level = dls.department_level  # Instance de DepartmentLevel
                description = str(dep_level)  # Utilise la méthode __str__
                filiere_list.append({
                    "id": dep_level.id,
                    "name": description,
                })
            return JsonResponse({"filieres": filiere_list}, status=200)
        else:
            return JsonResponse({"error": "Requête invalide."}, status=400)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return JsonResponse({"error": str(e)}, status=500)

class AvailabilityRequestListView(ListView):
    model = AvailabilityRequest
    template_name = 'availability/admin/availability_request_list.html'
    context_object_name = 'requests'

    def get_queryset(self):
        responses = AvailabilityResponse.objects.all()
        return AvailabilityRequest.objects.prefetch_related(Prefetch('responses', queryset=responses),'filieres').all()

@method_decorator([login_required, user_passes_test(lambda u: u.is_admin)], name='dispatch')
class CreateAvailabilityRequestView(View):
    """
    Affiche le formulaire de création d'une demande de disponibilité.
    """
    template_name = "availability/admin/request_forms.html"

    def get(self, request):
        subjects = Subject.objects.all()
        context = {
            'subjects': subjects,
            'form_action_url': reverse('availability:create_availability_request'),
        }
        return render(request, self.template_name, context)
    
# Fonction principale pour créer une demande de disponibilité
# @transaction.atomic
# def create_availability_request(request):
#     if request.method != "POST":
#         send_custom_message(request, _("Méthode non autorisée"), 'error')
#         return redirect('availability:create_request')

#     try:
#         subject_id = request.POST.get("subject_id")
#         teacher_ids_raw = request.POST.get("teacher_ids", "")
#         teacher_ids = teacher_ids_raw.split(",") if teacher_ids_raw else []
#         filiere_ids = request.POST.getlist("filiere_ids") 
#         start_date = request.POST.get("start_date")
#         end_date = request.POST.get("end_date")

        
#         if not subject_id or not teacher_ids or not start_date or not end_date or not filiere_ids:
#             send_custom_message(request, _("Données incomplètes. Veuillez vérifier les informations envoyées."), 'error')
#             return redirect('availability:create_request')

#         teacher_ids_validated, error_msg = validate_teacher_ids(teacher_ids)
#         if not teacher_ids_validated:
#             send_custom_message(request, _("IDs enseignants invalides. Vérifiez les identifiants des enseignants."), 'error')
#             return redirect('availability:create_request')

#         # Récupération de la matière et des enseignants associés
#         subject = get_object_or_404(Subject, id=subject_id)
#         teachers = TeacherProfile.objects.filter(id__in=teacher_ids_validated)
#         if not teachers.exists():
#             send_custom_message(request, _("Aucun enseignant valide trouvé. Vérifiez les IDs."), 'error')
#             return redirect('availability:create_request')

#         # Création de la demande avec les dates
#         availability_request = AvailabilityRequest.objects.create(
#             subject=subject,
#             start_date=start_date,
#             end_date=end_date)
#         availability_request.teachers.set(teachers)
#         availability_request.filieres.set(filiere_ids)

#         # Création d'une réponse "pending" pour chaque enseignant
#         responses = [
#             AvailabilityResponse(
#                 request=availability_request,
#                 teacher=teacher,
#                 status='pending') for teacher in teachers
#         ]
#         AvailabilityResponse.objects.bulk_create(responses)

#         send_custom_message(request, _("Demande de disponibilité créée avec succès !"), 'success')
#         return redirect('availability:availability_request_list')

#     except Exception as e:
#         send_custom_message(request, _("Erreur interne : {0}".format(str(e))), 'error')
#         return redirect('availability:create_request')

@transaction.atomic
def create_availability_request(request):
    if request.method != "POST":
        send_custom_message(request, _("Méthode non autorisée"), 'error')
        return redirect('availability:create_request')

    try:
        subject_id = request.POST.get("subject_id")
        teacher_ids_raw = request.POST.get("teacher_ids", "")
        teacher_ids = teacher_ids_raw.split(",") if teacher_ids_raw else []
        filiere_ids = request.POST.getlist("filiere_ids")
        start_date = request.POST.get("start_date")
        end_date = request.POST.get("end_date")

        if not subject_id or not teacher_ids or not start_date or not end_date or not filiere_ids:
            send_custom_message(request, _("Données incomplètes. Veuillez vérifier les informations envoyées."), 'error')
            return redirect('availability:create_request')

        teacher_ids_validated, error_msg = validate_teacher_ids(teacher_ids)
        if not teacher_ids_validated:
            send_custom_message(request, _("IDs enseignants invalides. Vérifiez les identifiants des enseignants."), 'error')
            return redirect('availability:create_request')

        subject = get_object_or_404(Subject, id=subject_id)
        teachers = TeacherProfile.objects.filter(id__in=teacher_ids_validated)
        if not teachers.exists():
            send_custom_message(request, _("Aucun enseignant valide trouvé. Vérifiez les IDs."), 'error')
            return redirect('availability:create_request')

        availability_request = AvailabilityRequest.objects.create(
            subject=subject,
            start_date=start_date,
            end_date=end_date
        )
        availability_request.teachers.set(teachers)
        availability_request.filieres.set(filiere_ids)

        responses = [
            AvailabilityResponse(
                request=availability_request,
                teacher=teacher,
                status='pending'
            ) for teacher in teachers
        ]
        AvailabilityResponse.objects.bulk_create(responses)

        send_custom_message(request, _("Demande de disponibilité créée avec succès !"), 'success')
        return redirect('availability:availability_request_list')

    except Exception as e:
        send_custom_message(request, _("Erreur interne : {0}".format(str(e))), 'error')
        return redirect('availability:create_request')

@method_decorator([login_required, user_passes_test(lambda u: u.is_admin)], name='dispatch')
class UpdateAvailabilityRequestView(View):
    """
    Affiche le formulaire de modification d'une demande de disponibilité.
    """
    template_name = "availability/admin/request_forms.html"

    def get(self, request, pk):
        availability_request = get_object_or_404(AvailabilityRequest, pk=pk)
        subjects = Subject.objects.all()
        context = {
            'subjects': subjects,
            'availability_request': availability_request,
            'form_action_url': reverse('availability:update_availability_request', args=[availability_request.pk]),
        }
        return render(request, self.template_name, context)

@transaction.atomic
def update_availability_request(request, pk):
    if request.method != "POST":
        send_custom_message(request, _("Méthode non autorisée"), 'error')
        return redirect('availability:availability_request_list')

    try:
        availability_request = get_object_or_404(AvailabilityRequest, pk=pk)
        
        # Vérifier si des réponses ont déjà été traitées (acceptées ou rejetées)
        if availability_request.responses.filter(status__in=['accepted', 'rejected']).exists():
            send_custom_message(request, _("Cette demande ne peut pas être modifiée car des réponses ont déjà été traitées."), 'error')
            return redirect('availability:availability_request_list')

        subject_id = request.POST.get("subject_id")
        teacher_ids_raw = request.POST.get("teacher_ids", "")
        teacher_ids = teacher_ids_raw.split(",") if teacher_ids_raw else []
        filiere_ids = request.POST.getlist("filiere_ids")
        start_date = request.POST.get("start_date")
        end_date = request.POST.get("end_date")

        if not subject_id or not teacher_ids or not start_date or not end_date or not filiere_ids:
            send_custom_message(request, _("Données incomplètes. Veuillez vérifier les informations envoyées."), 'error')
            return redirect('availability:availability_request_edit', pk=pk)

        teacher_ids_validated, error_msg = validate_teacher_ids(teacher_ids)
        if not teacher_ids_validated:
            send_custom_message(request, _("IDs enseignants invalides. Vérifiez les identifiants des enseignants."), 'error')
            return redirect('availability:availability_request_edit', pk=pk)

        subject = get_object_or_404(Subject, id=subject_id)
        teachers = TeacherProfile.objects.filter(id__in=teacher_ids_validated)
        if not teachers.exists():
            send_custom_message(request, _("Aucun enseignant valide trouvé. Vérifiez les IDs."), 'error')
            return redirect('availability:availability_request_edit', pk=pk)

        # Mise à jour de la demande
        availability_request.subject = subject
        availability_request.start_date = start_date
        availability_request.end_date = end_date
        availability_request.save()

        # Mise à jour des relations many-to-many
        availability_request.teachers.set(teachers)
        availability_request.filieres.set(filiere_ids)

        send_custom_message(request, _("Demande de disponibilité modifiée avec succès !"), 'success')
        return redirect('availability:availability_request_list')

    except Exception as e:
        send_custom_message(request, _("Erreur interne : {0}".format(str(e))), 'error')
        return redirect('availability:availability_request_edit', pk=pk)
        
class AvailabilityRequestDeleteView(DeleteView):
    model = AvailabilityRequest
    template_name = 'availability/admin/confirm_delete.html'
    context_object_name = 'availability_request'
    success_url = reverse_lazy('availability:availability_request_list')
    cancel_url = reverse_lazy('availability:availability_request_list')

    def delete(self, request, *args, **kwargs):
        availability_request = self.get_object()
        if availability_request.responses.filter(status__in=['accepted', 'rejected']).exists():
            send_custom_message(request, _("Cette demande ne peut pas être supprimée car elle a déjà des réponses."), 'error')
            return redirect(self.success_url)
        
        send_custom_message(request, _("Demande de disponibilité supprimée avec succès."), 'success')
        return super().delete(request, *args, **kwargs)

# Historique des demande en attente accepter ou rejeter 
class TeacherAvailabilityRequestListView(ListView):
    model = AvailabilityRequest
    template_name = 'availability/teacher/history_request.html'
    context_object_name = 'requests'

    def get_queryset(self):
        teacher = self.request.user.teacherprofile
        status_filter = self.request.GET.get('status', 'all')
        teacher_response_prefetch = Prefetch(
            'responses',
            queryset=AvailabilityResponse.objects.filter(teacher=teacher),
            to_attr='teacher_response'
        )
        queryset = AvailabilityRequest.objects.filter(
            responses__teacher=teacher
        ).prefetch_related(teacher_response_prefetch).distinct()

        if status_filter != 'all':
            queryset = queryset.filter(responses__status=status_filter)
        return queryset

    def render_to_response(self, context, **response_kwargs):
        # Si la requête est AJAX, renvoyer uniquement les données JSON
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            data = []
            for req in context['requests']:
                if hasattr(req, 'teacher_response') and req.teacher_response:
                    resp = req.teacher_response[0]
                    data.append({
                        'id': req.id,
                        'subject': req.subject.name,
                        'filieres': [str(f) for f in req.filieres.all()],
                        'period': req.start_date.strftime("%d/%m/%Y") + " - " + req.end_date.strftime("%d/%m/%Y"),
                        'created_at': timesince(req.created_at) + " ago",
                        'status': resp.status,
                        'url_accept': reverse('availability:accept_availability_request', args=[req.id]),
                        'url_reject': reverse('availability:reject_availability_request', args=[req.id]),
                    })
            return JsonResponse({'requests': data})
        return super().render_to_response(context, **response_kwargs)

class TeacherAvailabilityPendingRequestView(ListView):
    model = AvailabilityRequest
    template_name = 'availability/teacher/availability_pending.html'
    context_object_name = 'requests'

    def get_queryset(self):
        teacher = self.request.user.teacherprofile
        teacher_response_prefetch = Prefetch(
            'responses',
            queryset=AvailabilityResponse.objects.filter(teacher=teacher, status='pending'),
            to_attr='teacher_response'
        )
        # On filtre uniquement les demandes dont la réponse de l'enseignant est en attente
        queryset = AvailabilityRequest.objects.filter(responses__teacher=teacher, responses__status='pending').prefetch_related(teacher_response_prefetch).distinct()
        return queryset

# Fonction pour accepter une demande 
def accept_availability_request(request, request_id):
    # Récupérer la demande de disponibilité
    availability_request = get_object_or_404(AvailabilityRequest, pk=request_id)
    
    # Récupérer la réponse de l'enseignant concerné
    response = get_object_or_404(AvailabilityResponse, request=availability_request, teacher=request.user.teacherprofile)
    
    # Vérifier que l'enseignant est bien celui qui a répondu à la demande
    if response.teacher != request.user.teacherprofile:
        send_custom_message(request, _("Vous ne pouvez pas accepter ou rejeter cette demande."), 'error')
        return redirect('availability:teacher_availability_pending_request_list')
    
    # Mettre à jour le statut de la réponse à "accepté"
    response.status = 'accepted'
    response.save()

    # Message de succès
    send_custom_message(request, _("Demande acceptée avec succès."), 'success')

    # Redirection vers la liste des demandes en attente
    return redirect('availability:teacher_availability_pending_request_list')

# Fonction pour rejeter une demande 
def reject_availability_request(request, request_id):
    # Récupérer la demande de disponibilité
    availability_request = get_object_or_404(AvailabilityRequest, pk=request_id)
    
    # Récupérer la réponse de l'enseignant concerné
    response = get_object_or_404(AvailabilityResponse, request=availability_request, teacher=request.user.teacherprofile)
    
    # Vérifier que l'enseignant est bien celui qui a répondu à la demande
    if response.teacher != request.user.teacherprofile:
        send_custom_message(request, _("Vous ne pouvez pas accepter ou rejeter cette demande."), 'error')
        return redirect('availability:teacher_availability_pending_request_list')
    
    # Mettre à jour le statut de la réponse à "rejeté"
    response.status = 'rejected'
    response.save()

    # Message de succès
    send_custom_message(request, _("Demande rejetée avec succès."), 'error')

    # Redirection vers la liste des demandes en attente
    return redirect('availability:teacher_availability_pending_request_list')
