from django.http import JsonResponse
from django.utils.translation import gettext_lazy as _
from django.views.decorators.csrf import csrf_exempt

from apps.availability.models import AvailabilityRequest
from apps.home.utils import send_custom_message

# Fonction auxiliaire pour valider les IDs
def validate_teacher_ids(teacher_ids):
    if not teacher_ids:
        return False, _("Aucun ID d'enseignant fourni.")
    try:
        teacher_ids = list(map(int, teacher_ids))
    except ValueError:
        return False, _("Les IDs des enseignants doivent être des entiers valides.")
    return teacher_ids, None

def send_availability_request_notification(teachers, subject, filieres, days):
    filieres_names = ", ".join([filiere.name for filiere in filieres])
    days_list = ", ".join(days)
    
    message = f"Vous avez reçu une demande de disponibilité dans les matières : {subject.name}. "
    message += f"Les filières concernées sont : {filieres_names}. "
    message += f"Les jours suivants sont demandés : {days_list}. "
    message += "Merci de répondre à la demande via votre interface."

    for teacher in teachers:
        send_custom_message(teacher.user, message, 'info')

@csrf_exempt
def reset_filter(request):
    """
    Réinitialise le filtre des demandes et retourne toutes les demandes.
    """
    if request.is_ajax() and request.method == "POST":
        teacher = request.user.teacherprofile
        # On récupère toutes les demandes, sans appliquer de filtre sur le statut
        requests = AvailabilityRequest.objects.filter(responses__teacher=teacher)

        # Préparer les données à renvoyer en JSON
        data = {
            'requests': [
                {
                    'id': req.id,
                    'subject': req.subject.name,
                    'status': req.responses.filter(teacher=teacher).first().status,
                    'created_at': req.created_at.strftime('%d/%m/%Y'),
                }
                for req in requests
            ]
        }
        return JsonResponse(data, safe=False)

    return JsonResponse({"error": "Invalid request"}, status=400)

