import logging
from api.models import Permission
from social.pipeline import partial

log = logging.getLogger(__name__)


def set_roles_for_edx_users(user, permissions):
    '''
    This function create roles for proctors from sso permissions.
    '''

    permission_list = []
    for role in permissions:
        if role['obj_perm'] == [u'Proctoring']:
            permission_list.append(Permission(
                object_type=role['obj_type'],
                object_id=role['obj_id'],
                user=user
            )
            )
    Permission.objects.filter(user=user).delete()
    Permission.objects.bulk_create(permission_list)


@partial.partial
def create_or_update_permissions(backend, user, response, *args, **kwargs):
    permissions = response.get('permissions')
    if permissions is not None:
        try:
            set_roles_for_edx_users(user, permissions)
        except Exception as e:
            log.error(u'set_roles_for_edx_users error: {}'.format(e))

    return response
