from django.shortcuts import redirect, get_object_or_404

from apps.timetable.models import Timetable

def timetable_default_redirect(request):
    """
    Si on appelle /timetables/ sans ID, on redirige vers /timetables/<pk>/ 
    où <pk> est l'ID du dernier Timetable.
    """
    last_timetable = Timetable.objects.order_by('-start_date').first()
    if last_timetable:
        return redirect('timetables:timetable_detail', pk=last_timetable.pk)
    # S'il n'y a pas de Timetable en base, tu peux gérer autrement :
    return redirect('timetables:no_timetable_page')  # Ou afficher un message, etc.

from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from .models import Timetable

def download_timetable(request, pk):
    timetable = get_object_or_404(Timetable, pk=pk)
    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="Timetable_{timetable.start_date}.pdf"'
    
    # Ici, tu dois générer le PDF (ex: avec ReportLab)
    response.write("Génération du PDF en cours...")  # Placeholder

    return response

# def timetable_default_redirect(request):
#     last_timetable = Timetable.objects.order_by('-start_date').first()
#     if last_timetable:
#         return redirect('timetable_detail', pk=last_timetable.pk)
#     else:
#         # Soit on redirige vers une page d'accueil, ou on affiche un message autrement
#         return HttpResponse("Aucun Timetable n'est disponible.")
