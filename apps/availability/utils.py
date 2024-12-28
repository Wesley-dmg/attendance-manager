# from django.http import JsonResponse
# from django.shortcuts import get_object_or_404
# from subjects.models import Subject

# def get_teachers_for_subject(request):
#     if request.is_ajax() and 'subject_id' in request.GET:
#         subject_id = request.GET['subject_id']
#         subject = get_object_or_404(Subject, id=subject_id)
#         teachers = subject.teachers.all()
#         data = {
#             'teachers': [{'id': t.id, 'name': t.user.get_full_name()} for t in teachers],
#         }
#         return JsonResponse(data)
#     return JsonResponse({'error': 'Invalid request'}, status=400)
