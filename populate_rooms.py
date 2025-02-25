import os
import random
from faker import Faker
import django

# Configuration explicite de DJANGO_SETTINGS_MODULE
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

django.setup()  # Assure que Django est bien chargé si exécuté en script

from apps.rooms.models import Building, Floor, Room  # Import des modèles

fake = Faker("fr_FR")  # Faker en français

# Fonction pour créer des bâtiments
def create_buildings():
    """Crée des bâtiments fictifs avec des noms réalistes."""
    building_names = ["Bâtiment A", "Bâtiment B", "Bâtiment C", "Pavillon Sciences", "Centre Informatique"]
    buildings = []

    for name in building_names:
        building, created = Building.objects.get_or_create(name=name)
        if created:
            print(f'✅ Création du bâtiment {name}')
        else:
            print(f'⚡ Bâtiment {name} déjà existant')
        buildings.append(building)

    return buildings

# Fonction pour créer des étages
def create_floors(buildings):
    """Crée des étages (1 à 5) pour chaque bâtiment."""
    floors = []

    for building in buildings:
        for num in range(1, random.randint(2, 5)):  # Chaque bâtiment a 2 à 4 étages
            floor, created = Floor.objects.get_or_create(number=num, building=building)
            if created:
                print(f'✅ Création de l\'étage {num} pour le bâtiment {building.name}')
            else:
                print(f'⚡ Étage {num} déjà existant pour le bâtiment {building.name}')
            floors.append(floor)

    return floors

# Fonction pour créer des salles
def create_rooms(floors, num_rooms=50):
    """Crée des salles avec des numéros uniques par bâtiment."""
    room_counter = {}  # Pour éviter les doublons de numéros par bâtiment

    for floor in floors:
        if floor.building.name not in room_counter:
            room_counter[floor.building.name] = 100  # Numéros de salle commencent à 100

        for _ in range(random.randint(5, 15)):  # Chaque étage a 5 à 15 salles
            if num_rooms <= 0:
                return  # Stop si on atteint la limite

            room_number = room_counter[floor.building.name]
            room_counter[floor.building.name] += 1  # Incrémenter le numéro de salle

            # Vérifier si la salle existe déjà pour cet étage et ce numéro de salle
            if not Room.objects.filter(room_number=room_number, floor=floor).exists():
                room = Room.objects.create(
                    room_number=room_number,
                    floor=floor,
                    building=floor.building,
                    available=random.choice([True, False])  # Disponibilité aléatoire
                )
                print(f'✅ Création de la salle {room_number} sur l\'étage {floor.number} du bâtiment {floor.building.name}')
            else:
                print(f'⚡ Salle {room_number} déjà existante sur l\'étage {floor.number} du bâtiment {floor.building.name}')

            num_rooms -= 1

# Fonction principale pour exécuter la génération
def run():
    """Exécute la génération des données."""
    print("🔹 Génération des bâtiments...")
    buildings = create_buildings()

    print("🔹 Génération des étages...")
    floors = create_floors(buildings)

    print("🔹 Génération des salles...")
    create_rooms(floors, num_rooms=50)

    print("✅ 50 salles créées avec succès !")

if __name__ == "__main__":
    run()
