from django.db import migrations

CATEGORIES = [
    ('SU',        75, False, 3),
    ('A',    40, True,  2),
    ('L',          35, False, 2),
    ('JSU', 25, False, 1),
    ('ST',       25, True,  1),
    ('1',             9, False, 1),
    ('2',             9, False, 1),
    ('3',             9, False, 1),
    ('4',             9, False, 1),
    ('5',             9, False, 1),
]

def seed_categories(apps, _schema_editor):
    RoomCategory = apps.get_model('hotels', 'RoomCategory')
    for tier, min_area, requires_kitchen, min_rooms in CATEGORIES:
        RoomCategory.objects.get_or_create(
            tier=tier,
            defaults={
                'min_area': min_area,
                'requires_kitchen': requires_kitchen,
                'min_rooms': min_rooms,
            }
        )

class Migration(migrations.Migration):
    dependencies = [('hotels', '0008_roomcategory_alter_hotel_options_and_more')]
    operations = [migrations.RunPython(seed_categories, migrations.RunPython.noop)]
