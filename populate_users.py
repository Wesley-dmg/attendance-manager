import os
import django

# ⚠️ Assure-toi que "core.settings" correspond bien à ton projet
os.environ["DJANGO_SETTINGS_MODULE"] = "core.settings"

# 🔧 Charger Django après avoir défini les paramètres
django.setup()

from django.contrib.auth import get_user_model
from apps.users.models import TeacherProfile, StudentProfile, ParentProfile, AdminProfile, AdminType
from apps.courses.models import DepartmentLevel
from apps.subjects.models import Subject
from faker import Faker
import random

User = get_user_model()
fake = Faker('fr_FR')

def create_users():
    existing_admins = AdminProfile.objects.count()
    existing_teachers = TeacherProfile.objects.count()
    existing_parents = ParentProfile.objects.count()
    existing_students = StudentProfile.objects.count()

    max_admins = 10
    max_teachers = 25
    max_parents = 40
    max_students = 125

    roles_distribution = {
        'admin': max(0, max_admins - existing_admins),
        'teacher': max(0, max_teachers - existing_teachers),
        'parent': max(0, max_parents - existing_parents),
        'student': max(0, max_students - existing_students)
    }

    created_users = []

    for role, count in roles_distribution.items():
        if count == 0:
            print(f"🚫 Nombre maximum atteint pour {role}, aucune création supplémentaire.")
            continue

        for _ in range(count):
            user = User.objects.create(
                username=fake.unique.user_name(),
                first_name=fake.first_name(),
                last_name=fake.last_name(),
                email=fake.unique.email(),
                role=role,
                phone_number=fake.phone_number(),
                date_of_birth=fake.date_of_birth(minimum_age=18, maximum_age=60),
                address=fake.address(),
                password='password123'
            )
            user.set_password('password123')
            user.save()
            created_users.append(user)
            print(f"✅ Utilisateur {role} créé : {user.username}")

            if role == 'admin':
                admin_type = random.choice(AdminType.objects.all())
                AdminProfile.objects.create(user=user, admin_type=admin_type)
                print(f"🔹 Profil Administrateur créé : {user.username}")

            elif role == 'teacher':
                teacher = TeacherProfile.objects.create(
                    user=user, grade=random.choice(["Professeur", "Maître de Conférence"])
                )
                subjects = Subject.objects.order_by('?')[:random.randint(1, 3)]
                teacher.subjects.set(subjects)
                print(f"🔹 Profil Enseignant créé : {user.username} avec {len(subjects)} matières")

            elif role == 'student':
                department_level = DepartmentLevel.objects.order_by('?').first()
                student = StudentProfile.objects.create(user=user, major=department_level)
                print(f"🔹 Profil Étudiant créé : {user.username} ({department_level})")

            elif role == 'parent':
                parent = ParentProfile.objects.create(user=user)
                
                # Associer à des étudiants existants
                students = list(StudentProfile.objects.order_by('?')[:random.randint(1, 3)])
                if students:
                    parent.children.add(*students)
                    print(f"🔹 Parent {user.username} associé à {len(students)} enfant(s) : {[s.user.username for s in students]}")
                else:
                    print(f"⚠️ Aucun étudiant disponible pour le parent {user.username}")
    
    return created_users

if __name__ == "__main__":
    create_users()
