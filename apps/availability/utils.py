from django.utils.translation import gettext_lazy as _

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
