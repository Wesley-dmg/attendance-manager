import os
import django
from faker import Faker

# Configuration de Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from apps.courses.models import Department, Level, DepartmentLevel

# Initialisation de Faker en français
fake = Faker('fr_FR')

# Liste des filières disponibles en République du Bénin
benin_departments = [
    'Gestion des Ressources Humaines',
    'Commerce International',
    'Journalisme',
    'Hôtellerie et Tourisme',
    'Sciences Économiques',
    'Droit des Affaires',
    'Gestion des Projets',
    'Management des Organisations',
    'Entrepreneuriat',
    'Relations Internationales',
    'Administration Publique',
    'Sciences Politique',
    'Banque - Finance - Comptabilité',
    'Gestion des Entreprises et des Administrations',
    'Communication d\'Entreprise',
    'Marketing et Techniques de Commercialisation',
    'Génie Électrique et Informatique Industrielle',
    'Génie des Télécommunications et Réseaux',
    'Transport et Logistique',
    'Audit - Contrôle de Gestion - Fiscalité',
    'Droit',
    'Informatique Appliquée à la Gestion',
    'Informatique Réseaux et Télécommunications',
    'Génie Civil',
    'Sciences Agronomiques',
    'Techniques de l\'Audiovisuel et de la Communication'
]

# Création des niveaux d'études (s'ils n'existent pas)
level_names = ['L1', 'L2', 'L3', 'M1', 'M2']
try:
    levels = {level.name: level for level in Level.objects.all()}
except Exception as e:
    print(f"❌ Erreur lors du chargement des niveaux : {e}")
    levels = {}

for name in level_names:
    if name not in levels:
        level = Level.objects.create(name=name)
        levels[name] = level
        print(f'✅ Création du niveau {name}')
    else:
        print(f'⚡ Niveau {name} déjà existant')

# Création des départements et association avec les niveaux
for dept_name in benin_departments:
    department, created = Department.objects.get_or_create(
        name=dept_name,
        defaults={'description': fake.text()}  # Génère une description si le département est nouveau
    )

    if created:
        print(f'✅ Création du département {dept_name}')
    else:
        print(f'⚡ Département {dept_name} déjà existant')

    # Vérifier les niveaux déjà associés
    existing_levels = set(department.department_levels.values_list('level__name', flat=True))

    # Associer tous les niveaux (L1 à M2) si non déjà associés
    for level_name in level_names:
      if level_name not in existing_levels:
        _, created = DepartmentLevel.objects.get_or_create(department=department, level=levels[level_name])
        if created:
            print(f'  ➕ Association {dept_name} ↔ {level_name}')
        else:
            print(f'  🔄 Association {dept_name} ↔ {level_name} déjà existante')

print("\n🎉 Population terminée avec succès !")
