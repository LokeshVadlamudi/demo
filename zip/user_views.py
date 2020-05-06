from django.shortcuts import render
import pytz
from django.contrib import messages
from datetime import datetime
from .models import Vehicle,Customer,Reservation
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from .forms import UserCreateForm ,UserLoginForm, RentalBookingForm, RentalVehicleForm, UserEditForm, UserProfileEditForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout

# Create your views here.

def user_reservation(request):
    reservations=Reservation.objects.filter(user=request.user.username).order_by('-reservation_datetime')
    context={
        'reservations' : reservations
    }
    return render(request,'zip/reservation_details.html', context )


def user_search_view(request):
    form = request.GET
    user_search_query=form.get('user_search',None)
    users= Customer.objects.filter(first_name__contains=user_search_query)    
    context={
        'users' : users
    }

    return render(request,'zip/user_detail.html', context )

def user_create_view(request):    
    form = UserCreateForm(request.POST ,request.FILES)

    if form.is_valid():
        form.save()
        form=UserCreateForm()
    
    else:
        print('form error')

    context={
        'form' : form
    }
    # return render(request,' ', context)
    return render(request,'zip/user_create.html', context)

def user_view(request):
    users=Customer.objects.all()
    
    context={
        'users' : users
    }
    
    return render(request, 'zip/user_detail.html', context)


def user_login(request):
    form = UserLoginForm(request.POST, request.FILES)

    if form.is_valid():
        form.save()
        form = UserCreateForm()

    else:
        print('form error')

    context = {
        'form': form
    }

    return render(request, 'registration/login.html', context)

def user_search_form_view(request):
    return render(request, 'zip/user_search.html')

# def user_login(request):
#     return render(request, 'registration/login.html')

def user_register(request):
    return render(request, 'registration/register.html')

def user_dash(request):
    if request.method == 'POST':
        rental_booking_form = RentalBookingForm(data=request.POST)
        rental_vehicle_form = RentalVehicleForm(data=request.POST)
        if rental_booking_form.is_valid() and rental_vehicle_form.is_valid():
            reservation_datetime = rental_booking_form.cleaned_data['reservation_datetime']
            return_datetime = rental_booking_form.cleaned_data['return_datetime']
            tz = pytz.timezone('US/Pacific')
            time = datetime.now(tz).strftime('%Y-%m-%d %H:%M')
            if str(reservation_datetime) < time:
                messages.error(request,'Wrong Reservation Date!')
            if return_datetime <= reservation_datetime:
                messages.error(request,'Wrong Return Date!')
            if (return_datetime - reservation_datetime).days >= 3:
                messages.error(request,'Maximum 3 days allowed!')
            return HttpResponseRedirect('user_dash') 
    else:
        rental_booking_form = RentalBookingForm()
        rental_vehicle_form = RentalVehicleForm()
    return render(request, 'dashboards/userDash.html',{'rental_booking_form':rental_booking_form,
    'rental_vehicle_form':rental_vehicle_form})


def admin_dash(request):
    return render(request, 'dashboards/adminDash.html')

@login_required
def view_profile(request):
    customer = Customer.objects.get(user=request.user)

    context = {
        'user': request.user,
        'customer':customer
    }
    return render(request,'zip/profile.html',context)

def edit_profile(request):
    if request.method == 'POST':
        user_edit_form = UserEditForm(request.POST,instance=request.user)
        user_profile_edit_form = UserProfileEditForm(request.POST,instance=request.user)
        if user_edit_form.is_valid() and user_profile_edit_form.is_valid():
            user = user_edit_form.save()
            user.set_password(user.password)
            user.save()

            profile = user_profile_edit_form.save(commit=False)
            profile.user = user
            profile.save()
            messages.success(request,'User Profile Updated.')
            return HttpResponseRedirect('/zip/login')
    else:
        user_edit_form = UserEditForm(instance=request.user)
        user_profile_edit_form = UserProfileEditForm(instance=request.user)
        context = {
            'user_edit_form':user_edit_form,
            'user_profile_edit_form':user_profile_edit_form
        }
        return render(request,'zip/edit_profile.html',context)