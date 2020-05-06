from django.conf import settings
from django.utils import timezone
from creditcards.models import CardNumberField, CardExpiryField, SecurityCodeField
from django.utils.translation import gettext_lazy as _
from djongo import models
# from django import models as djangoModels
from django.contrib.auth.models import User
import uuid
from django.db.models.signals import post_save, post_init
from django.dispatch import receiver


# Create your models here.
class Location(models.Model):
    rental_location = models.CharField(max_length=200)
    rental_location_address = models.CharField(max_length=200)
    vehicle_capacity = models.IntegerField()
    no_of_vehicles = models.IntegerField(default=10)

    def __str__(self):
        return self.rental_location


class Vehicle(models.Model):
    # class VehicleType(models.ArrayField):
    #     SMALLCAR = 'SC', _('Small Car')
    #     FULLSIZECAR = 'FSC', _('Full Size Car')
    #     TRUCK = 'TR', _('Truck')
    #     LUXURYCAR = 'LC', _('Luxury Car')

    VehicleType = (
        ('SC', _('Small Car')),
        ('FSC', _('Full Size Car')),
        ('TR', _('Truck')),
        ('LC', _('Luxury Car')),
    )

    vehicle_type = models.CharField(
        max_length=3,
        choices=VehicleType,
        default='SC'
    )
    make_model = models.CharField(max_length=200)
    year = models.IntegerField()
    vin_no = models.CharField(max_length=50)
    registration_tag = models.CharField(max_length=20)
    current_mileage = models.IntegerField()
    last_service_time = models.DateField()

    basic_fee = models.IntegerField()
    advanced_fee = models.IntegerField()
    late_fee = models.IntegerField()

    # class VehicleCondition(models.TextChoices):
    #     GOOD = 'GD', _('Good')
    #     NEEDSCLEANING = 'NC', _('Needs Cleaning')
    #     NEEDSMAINTENANCE = 'NM', _('Needs Maintenance')

    VehicleCondition = (
        ('GD', _('Good')),
        ('NC', _('Needs Cleaning')),
        ('NM', _('Needs Maintenance')),
    )

    vehicle_condition = models.CharField(
        max_length=2,
        choices=VehicleCondition,
        default='GD',
    )

    rental_location = models.ForeignKey(Location, on_delete=models.CASCADE)
    previous_state = None

    @staticmethod
    def remember_state(sender, **kwargs):
        instance = kwargs.get('instance')

        #causing probs, please look
        # instance.previous_state = instance.rental_location

    def __str__(self):
        return self.vin_no


post_init.connect(Vehicle.remember_state, sender=Vehicle)


# sender is the Model after which save method the signal is called
@receiver(post_save, sender=Vehicle, dispatch_uid='signal_receiver')
def signal_receiver(sender, instance, created, **kwargs):
    if created:
        loc = Location.objects.get(rental_location=instance.rental_location)
        loc.no_of_vehicles = loc.no_of_vehicles - 1
    elif instance.previous_state != instance.rental_location:
        loc = Location.objects.get(rental_location=instance.rental_location)
        loc.no_of_vehicles = loc.no_of_vehicles - 1
        loc.save()
        loc = Location.objects.get(rental_location=instance.previous_state)
        loc.no_of_vehicles = loc.no_of_vehicles + 1
        loc.save()


class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=200)
    last_name = models.CharField(max_length=200)
    email_id = models.EmailField(max_length=200)
    driver_license_state = models.CharField(max_length=10)
    driving_license_no = models.CharField(max_length=200)
    date_of_birth = models.DateField()
    residence_address = models.CharField(max_length=500)
    cc_holder_name = models.CharField(max_length=200)
    cc_number = CardNumberField(_('Card Number'))
    cc_expiry = CardExpiryField(_('Expiration Date'))
    cc_code = SecurityCodeField(_('Security Code'))

    def __str__(self):
        return self.first_name + self.last_name


class Reservation(models.Model):
    # reservation_id = str(uuid.uuid1())
    user = models.CharField(max_length=200)
    vin_no = models.CharField(max_length=200)
    reservation_datetime = models.DateTimeField()
    rental_location = models.CharField(max_length=200)
    return_datetime = models.DateTimeField()
    rental_charge = models.CharField(max_length=100)
    actual_returntime = models.DateTimeField()

    # class ReservationStatus(models.TextChoices):
    #     BOOKED = 'BKD', _('BOOKED')
    #     RENTED = 'RNT', _('RENTED')
    #     RETURNED = 'RTD', _('RETURNED')

    ReservationStatus = (
        ('BKD', _('BOOKED')),
        ('RNT', _('RENTED')),
        ('RTD', _('RETURNED')),
    )

    reservation_status = models.CharField(
        max_length=3,
        choices=ReservationStatus,
        default='BKD',
    )

    def __str__(self):
        return self.user + self.vin_no + self.reservation_status


class Suggestion(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    reservation_id = models.ForeignKey(Reservation, on_delete=models.CASCADE)
    suggestion = models.TextField(max_length=200)
    VehicleCondition = (
        ('GD', _('Good')),
        ('NC', _('Needs Cleaning')),
        ('NM', _('Needs Maintenance')),
    )

    vehicle_condition = models.CharField(
        max_length=2,
        choices=VehicleCondition,
        default='GD',
    )

    def __str__(self):
        return self.suggestion
