import logging

from django.contrib.auth.models import User
from django.db import transaction
from person.models import Permission
from social.pipeline import partial

log = logging.getLogger(__name__)


@transaction.atomic
def set_roles_for_edx_users(user, permissions):
    '''
    This function create roles for proctors from sso permissions.
    '''
    proctor_perm = {
        u'Proctoring', u'*'
    }
    global_perm = {
        u'Read', u'Update', u'Delete', u'Publication', u'Enroll',
        u'Manage(permissions)'
    }
    permission_list = []
    for permission in permissions:
        if bool(set(permission['obj_perm']) & proctor_perm) or \
                global_perm.issubset(set(permission['obj_perm'])):
            role = Permission.ROLE_PROCTOR if bool(
                set(permission['obj_perm']) & proctor_perm
            ) else Permission.ROLE_INSTRUCTOR
            permission_list.append(
                Permission(
                    object_type=permission['obj_type'],
                    object_id=permission['obj_id'],
                    user=user,
                    role=role
                )
            )
    Permission.objects.filter(user=user).delete()
    Permission.objects.bulk_create(permission_list)


@partial.partial
def create_or_update_permissions(backend, user, response, *args, **kwargs):
    """
    Create or update permissions from SSO on every auth
    :return: Response
    """
    permissions = response.get('permissions')
    if permissions is not None:
        try:
            set_roles_for_edx_users(user, permissions)
        except Exception as e:
            print e
            log.error(u'set_roles_for_edx_users error: {}'.format(e))

    return response


@partial.partial
def update_user_name(backend, user, response, *args, **kwargs):
    """
    Ensure that we have the necessary information about a user (either an
    existing account or registration data) to proceed with the pipeline.
    """
    try:
            user = User.objects.get(email=response['email'])
            user.first_name = response.get('firstname')
            user.last_name = response.get('lastname')
            user.save()
    except User.DoesNotExist:
        pass

