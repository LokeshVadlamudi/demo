from django.shortcuts import render
from .models import Vehicle, Customer, Reservation, Suggestion, Location
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.db.models import Q
from .forms import *
import pytz
from django.contrib import messages
from datetime import datetime
from datetime import timedelta

# Create your views here.

def car_return_form(request, r_id,vin_no):
    retForm = VehicleReturnForm(request.POST or None)
    suggestionForm = VehicleReturnSuggestionForm(request.POST or None)
    reservation = Reservation.objects.get(id=r_id)

    # api here
    def calculate_rental_charge(initialResTime, initialRetTime, actualRetTime, rentPerHour1, rentPerHour2,
                                lateFee):
        finalFee = 0

        def calculateHours(a, b):
            print(type(a))
            seconds = a - b
            return seconds // 3600

        regularHours = calculateHours(initialRetTime.timestamp(), initialResTime.timestamp())
        extraHours = calculateHours(actualRetTime.timestamp(), initialRetTime.timestamp())
        base = 0
        advance = 0
        if regularHours > rentPerHour2[0]:
            finalFee += rentPerHour1[1] * rentPerHour1[2]
            base = finalFee
            finalFee += (regularHours - rentPerHour1[1]) * rentPerHour2[2]
            advance = finalFee - base
        else:
            finalFee += regularHours * rentPerHour1[2]
            base = finalFee
        chargeExtra = 0
        if extraHours > 0:
            chargeExtra = extraHours * lateFee
        print(base,advance)
        return base, advance, chargeExtra ,finalFee + chargeExtra

    vehicle = Vehicle.objects.get(vin_no=vin_no)
    base, advance, lateCharge,total = calculate_rental_charge(reservation.reservation_datetime, reservation.return_datetime,
                                                   reservation.actual_returntime, [1, 5, vehicle.basic_fee], [5, 72, vehicle.advanced_fee],
                                                   vehicle.late_fee)

    obj = {'base': base, 'advance': advance,'lateCharge':lateCharge, 'total': total}
    context = {
        'retForm': retForm,
        'reservation': reservation,
        'suggestionForm': suggestionForm,
        'obj': obj,
    }


    if retForm.is_valid() and request.user.is_authenticated and suggestionForm.is_valid():
        reservation = Reservation.objects.get(id=r_id)
        rental_location = reservation.rental_location
        loc = Location.objects.get(rental_location=rental_location)
        loc.no_of_vehicles = loc.no_of_vehicles + 1
        loc.save()

        print(reservation.reservation_status)
        reservation.reservation_status = 'RTD'
        reservation.actual_returntime = datetime.now()
        reservation.save()


        #change here


        suggestion = suggestionForm.cleaned_data['suggestion']
        Suggestion.objects.create(user=request.user, reservation_id=reservation, suggestion=suggestion)
        messages.success(request, 'Rental Vehicle Returned Successfully!!')
        return HttpResponseRedirect('/user_reservation')




    return render(request, 'zip/return_details.html', context)




def car_request_form(request, make_model, vin_no, rental_location):
    form = VehicleRequestForm(request.POST or None)
    context = {
        'form': form,
        'make_model': make_model,
        'vin_no': vin_no,
        'rental_location':rental_location
    }
    if form.is_valid() and request.user.is_authenticated:

        v = Vehicle.objects.get(vin_no=vin_no)
        rental_location = v.rental_location
        loc = Location.objects.get(rental_location=rental_location)
        loc.no_of_vehicles = loc.no_of_vehicles - 1
        loc.save()
        reservation_datetime = form.cleaned_data['reservation_datetime']
        return_datetime = form.cleaned_data['return_datetime']
        # print(reservation_datetime,return_datetime)
        rental_charge = 0
        tz = pytz.timezone('US/Pacific')
        time = datetime.now(tz).strftime('%Y-%m-%d %H:%M')
        if str(reservation_datetime) < time:
            messages.error(request, 'Wrong Reservation Date!')
            return HttpResponseRedirect(request.path_info)
        if return_datetime <= reservation_datetime:
            messages.error(request, 'Wrong Return Date!')
            return HttpResponseRedirect(request.path_info)
        if (return_datetime - reservation_datetime).days >= 3:
            messages.error(request, 'Maximum 3 days allowed!')
            return HttpResponseRedirect(request.path_info)
        flag = 0
        reservation_datetime = reservation_datetime.strftime('%Y-%m-%d %H:%M')
        return_datetime = return_datetime.strftime('%Y-%m-%d %H:%M')
        reservation_vin_location = Reservation.objects.filter(vin_no=vin_no).filter(rental_location=rental_location).filter(~Q(reservation_status="RTD")).all()
        if reservation_vin_location.count()!=0:
            reserved_time = Reservation.objects.filter(vin_no=vin_no).filter(rental_location=rental_location).filter(~Q(reservation_status="RTD")).values('reservation_datetime','return_datetime')
            start,end = [],[]
            for reserved in reserved_time:
                s = reserved['reservation_datetime']
                s = s.strftime("%Y-%m-%d %H:%M")
                start.append(s)
                e = reserved['return_datetime']
                e = e.strftime("%Y-%m-%d %H:%M")
                end.append(e)
            # messages.info(request,''+str(start)+str(end))
            start.sort()
            end.sort()
            if str(return_datetime)<=start[0]:
                flag = 1
            for i in range(len(end)-1):
                if str(reservation_datetime) >= end[i]:
                    if str(return_datetime) <= start[i+1]:
                        ## Reservation can be done
                        flag=1
            if str(reservation_datetime)>=end[-1]:
                flag=1
            if flag==1:
                reservation = Reservation(user=request.user.username, rental_location=rental_location,
                                  rental_charge=rental_charge, vin_no=vin_no,
                                  reservation_datetime=reservation_datetime, return_datetime=return_datetime)
                reservation.save()
                messages.success(request, "Thank you for the reservation. Enjoy you're ride!")
                return HttpResponseRedirect('/user_reservation')
            else:
                messages.info(request,'Reservation cannot be done at this location and time. Available vehicles at alternate locations.')
                reserved_vehicles = Reservation.objects.filter(reservation_datetime=reservation_datetime).filter(return_datetime=return_datetime).filter(rental_location=rental_location).filter(~Q(reservation_status="RTD")).values('vin_no')
                all_vehicles = Vehicle.objects.values('vin_no')
                rv,al = [],[]
                for vehicle in reserved_vehicles:
                    rv.append(vehicle['vin_no'])
                for vehicle in all_vehicles:
                    al.append(vehicle['vin_no'])
                available_vehicles = list(set(al)-set(rv))
                vehicles = Vehicle.objects.filter(pk__in=available_vehicles)
                context = {
                'vehicles': vehicles
                }
                return render(request, 'zip/car_detail.html', context)
        else:
            reservation = Reservation(user=request.user.username, rental_location=rental_location,
                                  rental_charge=rental_charge, vin_no=vin_no,
                                  reservation_datetime=reservation_datetime, return_datetime=return_datetime)
            reservation.save()
            messages.success(request, "Thank you for the reservation. Enjoy you're ride!")
            return HttpResponseRedirect('/user_reservation')
    return render(request, 'zip/car_request.html', context)


def car_search_form_view(request):
    if request.method == 'POST':
        form = VehicleSearchForm(request.POST)
        if form.is_valid():
            make_model_query = form.cleaned_data['make_model']
            rental_location_query = form.cleaned_data['rental_location']
            vehicle_type_query = form.cleaned_data['vehicle_type']
            vehicles = Vehicle.objects.filter(make_model__contains=make_model_query).filter(
                rental_location=rental_location_query).filter(vehicle_type__contains=vehicle_type_query)
            if vehicles.count() == 0:
                messages.error(request, make_model_query + ' vehicle is not available at ' + str(rental_location_query))
                alternate_location = Vehicle.objects.filter(make_model__contains=make_model_query).filter(
                    vehicle_type__contains=vehicle_type_query).first()
                vehicles = Vehicle.objects.filter(make_model__contains=make_model_query).filter(
                    vehicle_type__contains=vehicle_type_query).all()
                if alternate_location != None:
                    messages.success(request, 'The Vehicle is available at ' + str(alternate_location.rental_location))
            context = {
                'vehicles': vehicles
            }
            return render(request, 'zip/car_detail.html', context)

    form = VehicleSearchForm(request.POST or None)
    context = {
        'form': form
    }
    return render(request, 'zip/car_search.html', context)


def default_view(request):
    return render(request, 'base.html')


def locations_add_view(request):
    import csv
    global line
    path = '/Users/lokesh/Desktop/sp20-cmpe-202-sec-49-team-project-fourreal/locations.csv'

    with open(path) as f:
        reader = csv.reader(f)
        for row in reader:
            _, created = Location.objects.get_or_create(
                rental_location=row[0],
                rental_location_address=row[1],
                vehicle_capacity=row[2],
                no_of_vehicles=row[3],
            )


def car_view(request):
    # context={}
    vehicles = Vehicle.objects.all()

    context = {
        'vehicles': vehicles
    }
    return render(request, 'zip/car_detail.html', context)


# cancelling reservation
def cancel_reservation(request, r_id):
    reservation = Reservation.objects.get(id=r_id)
    currentTime = datetime.now()
    initialResTime = reservation.reservation_datetime

    seconds = (currentTime.timestamp() - initialResTime.timestamp())

    if -(seconds // 3600) <= 1:
        reservation.reservation_status = 'RTD'
        reservation.save()
        messages.success(request,"The Reservation has been cancelled successfully!")
        return HttpResponseRedirect('/user_reservation')
    else:
        reservation.reservation_status = 'RTD'
        reservation.save()
        ## Minimum one-hour charge applied
        messages.success(request,"The Reservation has been cancelled successfully!")
        return HttpResponseRedirect('/user_reservation')

# def car_request_view(request,car):

#     # User.objects.filer to see if user is legit or not
#     # See if car is available or not
#     # if user exists and car exists register it
#     if request.user.is_authenticated:
#         user=request.user.get_username()
#         status='Pending'
#         transaction=Reservation(user=user, car=car, status=status)
#         transaction.save()
#         return render(request, 'zip/car_search.html')
