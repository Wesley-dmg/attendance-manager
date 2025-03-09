from django.contrib import messages

def send_custom_message(request, message, message_type='info'):
    """
    Envoie un message personnalisé à l'utilisateur.

    :param request: L'objet request de la vue Django.
    :param message: Le message à afficher.
    :param message_type: Type de message ('success', 'info', 'warning', 'error').
    """
    message_types = {
        'success': messages.SUCCESS,
        'info': messages.INFO,
        'warning': messages.WARNING,
        'error': messages.ERROR,
    }

    # Vérifie si le type de message est valide
    if message_type in message_types:
        messages.add_message(request, message_types[message_type], message)
    else:
        messages.add_message(request, messages.INFO, message)

