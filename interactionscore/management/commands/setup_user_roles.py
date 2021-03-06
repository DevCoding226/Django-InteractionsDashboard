from django.core.management.base import BaseCommand, CommandError
from django.contrib.contenttypes.models import ContentType
# from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission, Group

from interactionscore.models import (
    EngagementPlan,
    EngagementPlanPerms,
    Interaction,
    InteractionPerms,
)

# User = get_user_model()


USER_ROLES = {
    'MSL': [
        (EngagementPlan, EngagementPlanPerms.change_own_current_ep),
        (EngagementPlan, 'add_engagementplan'),
        (Interaction, 'add_interaction'),
    ],
    'MSL Manager': [
        (EngagementPlan, EngagementPlanPerms.list_own_ag_ep),
        (EngagementPlan, EngagementPlanPerms.approve_own_ag_ep),
        (Interaction, InteractionPerms.list_all_interaction)
    ],
}


class Command(BaseCommand):
    help = 'Setup Standard User roles and their permissions'

    def add_arguments(self, parser):
        parser.add_argument('--delete_old_groups', dest='delete_old_groups', action='store_true')
        parser.set_defaults(delete_old_groups=False)
        parser.add_argument('--delete_old_permissions', dest='delete_old_permissions', action='store_true')
        parser.set_defaults(delete_old_permissions=False)
        parser.add_argument('--create_new_permissions', dest='create_new_permissions', action='store_true')
        parser.set_defaults(create_new_permissions=False)

    def handle(self, *args, **options):

        if options['delete_old_groups']:
            self.stdout.write('Deleting old Groups...')
            Group.objects.filter(name__icontains='Role').delete()

        if options['delete_old_permissions']:
            self.stdout.write('Deleting old Permissions...')
            Permission.objects.filter(codename__in=self._get_perms_codes()).delete()

        self.stdout.write('Creating new Groups and Permissions...')
        for name, perm_opts in USER_ROLES.items():
            group, created_group = Group.objects.get_or_create(name='Role ' + name)
            if created_group:
                self.stdout.write('- created group ' + group.name)
            for model_class, perm_opt in perm_opts:
                perm_codename = perm_opt if type(perm_opt) is str else perm_opt.name
                perm_name = perm_opt if type(perm_opt) is str else perm_opt.value
                if options['create_new_permissions']:
                    self.stdout.write('- creating permission {}: {}'.format(perm_codename,
                                                                            perm_name))
                    ct = ContentType.objects.get_for_model(model_class)
                    perm = Permission.objects.create(codename=perm_codename,
                                                     name=perm_name,
                                                     content_type=ct)
                else:
                    perm = Permission.objects.get(codename=perm_codename)

                self.stdout.write('- adding permission {} to group {}'.format(perm_codename,
                                                                              group.name))
                group.permissions.add(perm)

        self.stdout.write(self.style.SUCCESS('...done!'))

    def _get_perms(self):
        return EngagementPlan.Meta.permissions

    def _get_perms_codes(self):
        return [p[0] for p in self._get_perms()]
