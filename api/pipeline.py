import logging
from api.models import Permission
from social.pipeline import partial

log = logging.getLogger(__name__)


def set_roles_for_edx_users(user, permissions):
    '''
    This function is specific functional for open-edx platform.
    It create roles for edx users from sso permissions.
    '''

    log_message = 'For User: {}, object_type {} and object_id {} there is not matched Role for Permission set: {}'

    global_perm = {'Read', 'Update', 'Delete', 'Publication', 'Enroll',
                   'Manage(permissions)'}
    staff_perm = {'Read', 'Update', 'Delete', 'Publication', 'Enroll'}
    tester_perm = {'Read', 'Enroll'}

    new_role_ids = []

    is_global_staff = False
    for role in permissions:
        _log = False
        if role['obj_perm'] == '*':
            Permission.objects.update_or_create(
                object_type=role['obj_type'],
                object_id=role['obj_id'],
            )

            #         elif 'Create' in role['obj_perm']:
            #             if not CourseCreatorRole().has_user(user):
            #                 CourseCreatorRole().add_users(user)
            #             car = CourseAccessRole.objects.get(user=user, role=CourseCreatorRole.ROLE)
            #             new_role_ids.append(car.id)
            #
            #         if role['obj_perm'] != '*' and global_perm != set(role['obj_perm']) and ['Create'] != role['obj_perm']:
            #             _log = True
            #
            #     elif role['obj_type'] == 'edxorg':
            #         if '*' in role['obj_perm'] or global_perm.issubset(set(role['obj_perm'])):
            #             if not OrgInstructorRole(role['obj_id']).has_user(user):
            #                 OrgInstructorRole(role['obj_id']).add_users(user)
            #             car = CourseAccessRole.objects.get(user=user,
            #                                                role=OrgInstructorRole(role['obj_id'])._role_name,
            #                                                org=role['obj_id'])
            #             new_role_ids.append(car.id)
            #
            #         elif staff_perm.issubset(set(role['obj_perm'])):
            #             if not OrgStaffRole(role['obj_id']).has_user(user):
            #                 OrgStaffRole(role['obj_id']).add_users(user)
            #             car = CourseAccessRole.objects.get(user=user, role=OrgStaffRole(role['obj_id'])._role_name,
            #                                                org=role['obj_id'])
            #             new_role_ids.append(car.id)
            #
            #         elif 'Read' in role['obj_perm']:
            #             if not OrgLibraryUserRole(role['obj_id']).has_user(user):
            #                 OrgLibraryUserRole(role['obj_id']).add_users(user)
            #             car = CourseAccessRole.objects.get(user=user, role=OrgLibraryUserRole.ROLE, org=role['obj_id'])
            #             new_role_ids.append(car.id)
            #
            #         if role['obj_perm'] != '*' and global_perm != set(role['obj_perm']) and \
            #                 staff_perm != set(role['obj_perm']) and 'Read' not in role['obj_perm']:
            #             _log = True
            #
            #     elif role['obj_type'] in ['edxcourse', 'edxlibrary']:
            #
            #         course_key = CourseKey.from_string(role['obj_id'])
            #
            #         if '*' in role['obj_perm'] or global_perm.issubset(set(role['obj_perm'])):
            #             if not CourseInstructorRole(course_key).has_user(user):
            #                 CourseInstructorRole(course_key).add_users(user)
            #             car = CourseAccessRole.objects.get(user=user, role=CourseInstructorRole.ROLE, course_id=course_key)
            #             new_role_ids.append(car.id)
            #
            #         elif staff_perm.issubset(set(role['obj_perm'])):
            #             if not CourseStaffRole(course_key).has_user(user):
            #                 CourseStaffRole(course_key).add_users(user)
            #             car = CourseAccessRole.objects.get(user=user, role=CourseStaffRole.ROLE, course_id=course_key)
            #             new_role_ids.append(car.id)
            #
            #         elif tester_perm.issubset(set(role['obj_perm'])):
            #             if not CourseBetaTesterRole(course_key).has_user(user):
            #                 CourseBetaTesterRole(course_key).add_users(user)
            #             car = CourseAccessRole.objects.get(user=user, role=CourseBetaTesterRole.ROLE, course_id=course_key)
            #             new_role_ids.append(car.id)
            #
            #         elif role['obj_type'] == 'edxlibrary' and 'Read' in role['obj_perm']:
            #             if not LibraryUserRole(course_key).has_user(user):
            #                 LibraryUserRole(course_key).add_users(user)
            #             car = CourseAccessRole.objects.get(user=user, role=CourseBetaTesterRole.ROLE, course_id=course_key)
            #             new_role_ids.append(car.id)
            #
            #         if role['obj_perm'] != '*' and global_perm != set(role['obj_perm']) and \
            #             staff_perm != set(role['obj_perm']) and tester_perm != set(role['obj_perm']) and 'Read' not in role['obj_perm']:
            #             _log = True
            #
            #     elif role['obj_type'] == 'edxcourserun':
            #
            #         course_key = CourseKey.from_string(role['obj_id'])
            #
            #         if '*' in role['obj_perm'] or global_perm.issubset(set(role['obj_perm'])):
            #             if not CourseInstructorRole(course_key).has_user(user):
            #                 CourseInstructorRole(course_key).add_users(user)
            #             car = CourseAccessRole.objects.get(user=user, role=CourseInstructorRole.ROLE, course_id=course_key)
            #             new_role_ids.append(car.id)
            #         elif staff_perm.issubset(set(role['obj_perm'])):
            #             if not CourseStaffRole(course_key).has_user(user):
            #                 CourseStaffRole(course_key).add_users(user)
            #             car = CourseAccessRole.objects.get(user=user, role=CourseStaffRole.ROLE, course_id=course_key)
            #             new_role_ids.append(car.id)
            #         elif tester_perm.issubset(set(role['obj_perm'])):
            #             if not CourseBetaTesterRole(course_key).has_user(user):
            #                 CourseBetaTesterRole(course_key).add_users(user)
            #             car = CourseAccessRole.objects.get(user=user, role=CourseBetaTesterRole.ROLE, course_id=course_key)
            #             new_role_ids.append(car.id)
            #
            #         if role['obj_perm'] != '*' and global_perm != set(role['obj_perm']) and \
            #             staff_perm != set(role['obj_perm']) and tester_perm != set(role['obj_perm']):
            #             _log = True
            #
            #     if _log:
            #         logging.warning(log_message.format(user.id, role['obj_type'], role['obj_id'], str(role['obj_perm'])))
            #
            # if (not is_global_staff) and GlobalStaff().has_user(user):
            #     GlobalStaff().remove_users(user)
            #
            # remove_roles = role_ids - set(new_role_ids)
            #
            # if remove_roles:
            #     entries = CourseAccessRole.objects.exclude(
            #         course_id__icontains='library').filter(id__in=list(remove_roles))
            #     entries.delete()


@partial.partial
def create_or_update_permissions(backend, user, response, *args, **kwargs):
    permissions = response.get('permissions')
    if permissions is not None:
        try:
            set_roles_for_edx_users(user, permissions)
        except Exception as e:
            log.error(u'set_roles_for_edx_users error: {}'.format(e))

    return response
