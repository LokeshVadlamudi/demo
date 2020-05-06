from builtins import set
from django import forms
from .models import Vehicle, Customer, Reservation, Location, Suggestion
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from bootstrap_datepicker_plus import DateTimePickerInput


class DateInput(forms.DateInput):
    input_type = 'date'



class VehicleReturnForm(forms.ModelForm):
     # = forms.CharField(widget=forms.CharField)
    # suggestion=forms.CharField(widget=forms.Textarea)
    class Meta:
        model = Vehicle
        fields = [
            'vehicle_condition',
        ]


class VehicleReturnSuggestionForm(forms.ModelForm):
    # = forms.CharField(widget=forms.CharField)
    class Meta:
        model = Suggestion
        fields = [
            'suggestion',
            'vehicle_condition'
        ]


class UserCreateForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = Customer
        fields = [
            'first_name',
            'last_name',
            'driving_license_no',
            'password'
        ]


class UserLoginForm(forms.ModelForm):
    email = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control text-box', 'title': 'username'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'user_login form-control text-box'}))

    class Meta:
        model = User
        fields = ('email', 'password')


class VehicleRequestForm(forms.ModelForm):
    reservation_datetime = forms.DateTimeField(widget=DateTimePickerInput())
    return_datetime = forms.DateTimeField(widget=DateTimePickerInput())

    labels = {
        'rental_location': _('Rental Location'),
        'reservation_datetime': _('Reservation Datetime'),
        'return_datetime': _('Return Datetime')
    }

    class Meta:
        model = Reservation
        fields = [
            'reservation_datetime',
            'return_datetime'
        ]


class VehicleSearchForm(forms.ModelForm):
    vehicles = Vehicle.objects.all()
    make_CHOICES = set()
    for vehicle in vehicles:
        make_CHOICES.add((vehicle.make_model, vehicle.make_model))

    make_model = forms.ChoiceField(choices=make_CHOICES)

    class Meta:
        model = Vehicle
        fields = [
            'vehicle_type',
            'rental_location',
            'make_model',
        ]


class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())

    class Meta:
        model = User
        fields = ('username', 'password', 'email')


class UserProfileInfoForm(forms.ModelForm):
    class Meta:
        model = Customer
        labels = {
            'cc_holder_name': _('Credit Card Holder Name'),
            'driving_license_no': _('Driving License Number')
        }
        fields = [
            'first_name',
            'last_name',
            'driving_license_no',
            'cc_holder_name',
            'cc_number',
            'cc_expiry',
            'cc_code'
        ]

class UserEditForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())

    class Meta:
        model = User
        fields = ('username', 'password', 'email')

class UserProfileEditForm(forms.ModelForm):
    class Meta:
        model = Customer
        labels = {
            'cc_holder_name': _('Credit Card Holder Name'),
            'driving_license_no': _('Driving License Number')
        }
        fields = [
            'first_name',
            'last_name',
            'driving_license_no',
            'cc_holder_name',
            'cc_number',
            'cc_expiry',
            'cc_code'
        ]


class RentalBookingForm(forms.ModelForm):
    reservation_datetime = forms.DateTimeField(widget=DateTimePickerInput())
    return_datetime = forms.DateTimeField(widget=DateTimePickerInput())
    labels = {
        'rental_location': _('Rental Location'),
        'reservation_datetime': _('Reservation Datetime'),
        'return_datetime': _('Return Datetime')
    }

    class Meta:
        model = Reservation
        fields = [
            'rental_location',
            'reservation_datetime',
            'return_datetime'
        ]


class RentalVehicleForm(forms.ModelForm):
    class Meta:
        model = Vehicle
        fields = [
            'vehicle_type',
        ]
