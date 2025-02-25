import os
import django

# ⚠️ Remplace 'core.settings' par ton vrai module de configuration si nécessaire
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")

# 🔧 Charger Django après avoir défini les paramètres
django.setup()

import random
from django.utils import timezone
from datetime import timedelta, time
from faker import Faker
from apps.subjects.models import Subject
from apps.users.models import TeacherProfile
from apps.courses.models import DepartmentLevel
from apps.rooms.models import Room
from apps.timetable.models import TimeSlot, Timetable, CourseSession

fake = Faker('fr_FR')

def create_time_slots():
    """
    Génère des créneaux horaires standards.
    """
    time_slots = [
        (time(8, 0), time(10, 0)),
        (time(10, 15), time(12, 15)),
        (time(13, 30), time(15, 30)),
        (time(15, 45), time(17, 45))
    ]
    
    created_slots = []
    for start_time, end_time in time_slots:
        slot, created = TimeSlot.objects.get_or_create(
            start_time=start_time,
            end_time=end_time,
            defaults={"label": f"{start_time.strftime('%H:%M')} - {end_time.strftime('%H:%M')}"}
        )
        if created:
            print(f"✅ Créneau ajouté : {slot.label}")
        created_slots.append(slot)
    
    return created_slots

def create_timetables(n=5):
    """
    Crée plusieurs emplois du temps pour différentes périodes et niveaux.
    """
    department_levels = list(DepartmentLevel.objects.all())
    if not department_levels:
        print("🚫 Pas de niveaux de départements disponibles.")
        return []
    
    timetables = []
    for _ in range(n):
        start_date = fake.date_between(start_date="-30d", end_date="+30d")
        end_date = start_date + timedelta(days=30)
        selected_levels = random.sample(department_levels, min(len(department_levels), random.randint(1, 3)))

        timetable = Timetable.objects.create(
            start_date=start_date,
            end_date=end_date
        )
        timetable.department_levels.set(selected_levels)
        timetable.save()

        print(f"📅 Emploi du temps créé : {timetable.start_date} - {timetable.end_date}")
        timetables.append(timetable)
    
    return timetables

def create_course_sessions(n=50):
    """
    Génère des sessions de cours en associant professeurs, matières, salles et créneaux horaires.
    """
    subjects = list(Subject.objects.all())
    teachers = list(TeacherProfile.objects.all())
    rooms = list(Room.objects.filter(available=True))
    timetables = list(Timetable.objects.all())
    time_slots = list(TimeSlot.objects.all())

    if not (subjects and teachers and rooms and timetables and time_slots):
        print("🚫 Données insuffisantes pour générer des sessions de cours.")
        return
    
    for _ in range(n):
        timetable = random.choice(timetables)
        subject = random.choice(subjects)
        teacher = random.choice(teachers)
        room = random.choice(rooms)
        timeslot = random.choice(time_slots)
        course_date = fake.date_between(start_date=timetable.start_date, end_date=timetable.end_date)

        session = CourseSession.objects.create(
            timetable=timetable,
            subject=subject,
            teacher=teacher,
            room=room,
            date=course_date,
            timeslot=timeslot
        )
        # Marquer la salle comme occupée
        room.available = False
        room.save()

        print(f"📖 Session créée : {subject.name} | {course_date} | {timeslot}")

if __name__ == "__main__":
    create_time_slots()
    create_timetables(n=5)
    create_course_sessions(n=50)
