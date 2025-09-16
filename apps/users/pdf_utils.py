import os
from django.conf import settings
from django.contrib.staticfiles import finders


def link_callback(uri, rel):
    """
    Convertit les liens statiques/médias en chemins absolus pour xhtml2pdf.
    """
    # 1) Si c'est une URL absolue (http:// ou https://)
    if uri.startswith("http://") or uri.startswith("https://"):
        return uri

    # 2) Si c'est un fichier statique
    if uri.startswith(settings.STATIC_URL):
        path = uri.replace(settings.STATIC_URL, "")
        absolute_path = finders.find(path)
        if absolute_path:
            return absolute_path
        return os.path.join(settings.STATIC_ROOT, path)

    # 3) Si c'est un fichier média
    if settings.MEDIA_URL and uri.startswith(settings.MEDIA_URL):
        path = uri.replace(settings.MEDIA_URL, "")
        return os.path.join(settings.MEDIA_ROOT, path)

    # 4) Sinon, retourne l'uri original (dernier recours)
    return uri
