from django.contrib import admin
from .models import Vehicle, Customer, Reservation, Location, Suggestion

admin.site.site_header = 'Four Real Zip Car'

# Register your models here.

admin.site.register(Vehicle)
admin.site.register(Customer)
admin.site.register(Reservation)
admin.site.register(Location)
admin.site.register(Suggestion)




