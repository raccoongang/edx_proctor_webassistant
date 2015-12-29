from django.test import TestCase
from journaling.admin import JournalingAdmin
from journaling.models import Journaling


class JournalingAdminTestCase(TestCase):
    def test_has_add_permission(self):
        request = Request()
        admin = JournalingAdmin(Journaling, request)
        self.assertFalse(admin.has_add_permission(request))

    def test_has_delete_permission(self):
        request = Request()
        admin = JournalingAdmin(Journaling, request)
        self.assertFalse(admin.has_delete_permission(request))

class Request():
    pass
