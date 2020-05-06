from django.test import TestCase
from zip.models import Location
# Create your tests here.

class LocationTestCase(TestCase):
    def setUp(self):
        Location.objects.create(rental_location="san jose", rental_location_address="sunny vale")
        Location.objects.create(rental_location="san francisco", rental_location_address="market street")
    def test_locations(self):
        rentalAddress = Location.objects.get(rental_location="san jose")
        self.assertEqual(rentalAddress.rental_location_address, "sunny vale")
        rentalAddress = Location.objects.get(rental_location="san francisco")
        self.assertEqual(rentalAddress.rental_location_address, "market street")

# class vehicleTestCase(TestCase):
#     def setUp(self):
#         Vehicle.objects.create(make_model="tesla3", year=2019)
#         Vehicle.objects.create(make_model="audi", year=2018)
#     def test_locations(self):
#         v1 = Vehicle.objects.get(make_model="tesla3")
#         self.assertEqual(v1.year, 2019)
#         v2 = Vehicle.objects.get(make_model="audi")
#         self.assertEqual(v2.year, 2018)