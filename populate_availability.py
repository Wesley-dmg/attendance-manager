import os
import django

# ⚠️ Remplace 'core.settings' par ton vrai module de configuration si différent
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")

# 🔧 Charger Django après avoir défini les paramètres
django.setup()

import random
from django.utils import timezone
from faker import Faker
from apps.subjects.models import Subject
from apps.users.models import TeacherProfile
from apps.courses.models import DepartmentLevel
from apps.availability.models import AvailabilityRequest, AvailabilityResponse


fake = Faker('fr_FR')

def create_availability_requests(n=20):
    subjects = list(Subject.objects.all())
    teachers = list(TeacherProfile.objects.all())
    filieres = list(DepartmentLevel.objects.all())
    
    if not subjects or not teachers or not filieres:
        print("🚫 Pas assez de données existantes pour créer des demandes de disponibilité.")
        return
    
    created_requests = []
    for _ in range(n):
        subject = random.choice(subjects)
        start_date = fake.date_between(start_date="-30d", end_date="+30d")
        end_date = start_date + timezone.timedelta(days=random.randint(7, 30))
        selected_teachers = random.sample(teachers, min(len(teachers), random.randint(1, 3)))
        selected_filieres = random.sample(filieres, min(len(filieres), random.randint(1, 2)))
        
        request = AvailabilityRequest.objects.create(
            subject=subject,
            start_date=start_date,
            end_date=end_date,
        )
        request.teachers.set(selected_teachers)
        request.filieres.set(selected_filieres)
        request.save()
        created_requests.append(request)
        
        print(f"✅ Demande de disponibilité créée : {subject.name} ({start_date} - {end_date})")
    
    return created_requests

def create_availability_responses():
    requests = AvailabilityRequest.objects.all()
    if not requests:
        print("🚫 Aucune demande de disponibilité pour créer des réponses.")
        return
    
    for request in requests:
        for teacher in request.teachers.all():
            status = random.choice(["accepted", "rejected", "pending"])
            response, created = AvailabilityResponse.objects.get_or_create(
                request=request,
                teacher=teacher,
                defaults={"status": status}
            )
            if created:
                print(f"🔹 Réponse créée : {teacher.user.username} - {status} pour {request.subject.name}")

if __name__ == "__main__":
    create_availability_requests(n=126)
    create_availability_responses()
