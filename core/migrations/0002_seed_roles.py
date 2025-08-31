from django.db import migrations

def seed_roles(apps, schema_editor):
    Role = apps.get_model("core", "Role")
    for role_name in ["Admin", "Passenger", "Conductor"]:
        Role.objects.get_or_create(name=role_name)

class Migration(migrations.Migration):

    dependencies = [
        ("core", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(seed_roles),
    ]
