from django.test import TestCase
from zip.models import Customer

class customerTestCase(TestCase):
    def setUp(self):
        Customer.objects.create(last_name="admin", first_name='lokesh')
        # Customer.objects.create(user="admin", first_name='lokesh')
    def test_vehicles(self):
        v1 = Customer.objects.get(last_name="admin")
        self.assertEqual(v1.first_name, 'lokesh')