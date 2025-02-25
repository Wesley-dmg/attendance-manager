import os
import django
import sys
from faker import Faker
import random

# Ajouter le chemin du projet Django pour éviter les erreurs d'import
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Initialiser les settings de Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from apps.subjects.models import Subject
from apps.courses.models import Department, DepartmentLevel
from apps.common.models import DepartmentLevelSubject

# Initialiser Faker
fake = Faker('fr_FR')  # Pour générer des données en français
Faker.seed(0)  # Optionnel, pour garantir la reproductibilité

# Récupérer toutes les filières existantes
departments = Department.objects.all()

# Créer des matières fictives
def create_fake_subjects(num_subjects=50):
    subjects = []
    for _ in range(num_subjects):
        # Créer une matière fictive
        subject_name = fake.bs()  # Utilise bs() de Faker pour générer un nom de matière "business speak"
        subject_code = fake.unique.lexify(text='???-#####')  # Générer un code unique comme "ABC-12345"
        
        # Créer et enregistrer la matière
        subject, created = Subject.objects.get_or_create(name=subject_name, code=subject_code)
        if created:
            subjects.append(subject)
            print(f"Matière créée : {subject.name} ({subject.code})")
    
    return subjects

# Associer les matières aux départements et niveaux de manière aléatoire
def associate_subjects_to_departments(subjects):
    for department in departments:
        # Récupérer les niveaux associés à ce département
        levels = DepartmentLevel.objects.filter(department=department)

        for subject in subjects:
            # Choisir un niveau aléatoire parmi les niveaux du département
            level = random.choice(levels)

            # Créer l'association entre la matière, le niveau et le département
            department_level_subject, created = DepartmentLevelSubject.objects.get_or_create(
                department_level=level,
                subject=subject
            )
            if created:
                print(f"Association créée : {subject.name} -> {department.name} ({level.level.name})")

# Générer les matières fictives et les associer
subjects = create_fake_subjects(num_subjects=60)  # Tu peux ajuster le nombre de matières à générer
associate_subjects_to_departments(subjects)
