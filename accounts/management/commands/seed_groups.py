from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission

GROUPS = {
    "Nurse": [
        # can add observation sets
        ("observations", "add_observationset"),
        ("observations", "change_observationset"),
        ("observations", "view_observationset"),
        ("patients", "view_patient"),
        ("patients", "view_encounter"),
        ("patients", "add_patient"),
        ("patients", "add_encounter"),
        ("patients", "change_patient"),
        ("patients", "change_encounter"),
        ("risk", "view_riskassessment"),
    ],
    "Doctor": [
        ("patients", "view_patient"),
        ("patients", "view_encounter"),
        ("observations", "view_observationset"),
        ("risk", "add_riskassessment"),
        ("risk", "view_riskassessment"),
    ],
    "Admin": [
        # admins will typically be staff/superuser, but we keep group for completeness
    ],
}

class Command(BaseCommand):
    help = "Create default hospital groups and assign basic permissions."

    def handle(self, *args, **options):
        for group_name, perms in GROUPS.items():
            group, _ = Group.objects.get_or_create(name=group_name)
            for app_label, codename in perms:
                try:
                    perm = Permission.objects.get(content_type__app_label=app_label, codename=codename)
                    group.permissions.add(perm)
                except Permission.DoesNotExist:
                    self.stdout.write(self.style.WARNING(f"Permission missing: {app_label}.{codename}"))
            self.stdout.write(self.style.SUCCESS(f"Ensured group: {group_name}"))
        self.stdout.write(self.style.SUCCESS("Done."))
