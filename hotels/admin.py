from django.contrib import admin
from hotels.models import HotelDataModel, Booking, Room # Import Booking
from django.utils.html import format_html

# customize the admin display for HotelDataModel (optional but recommended)
class HotelAdmin(admin.ModelAdmin):
    list_display = ('name', 'city', 'price', 'owner','image_preview','image_preview2','image_preview3','image_preview4')
    search_fields = ('name', 'city')
    list_filter = ('city', 'badge')

    def image_preview(self,obj):
        if obj.image:
            return format_html('<img src="{}" width="100" height="100" style="object-fit: cover;"/>',
                               obj.image.url
                               )
        return " No image !!!"
    image_preview.short_description = 'image'

    def image_preview2(self,obj):
        if obj.room_image1:
            return format_html('<img src="{}" width="100" height="100" style="object-fit: cover;"/>',
                               obj.room_image1.url
                               )
        return " No image !!!"
    image_preview2.short_description = 'image'

    def image_preview3(self,obj):
        if obj.room_image2:
            return format_html('<img src="{}" width="100" height="100" style="object-fit: cover;"/>',
                               obj.room_image2.url
                               )
        return " No image !!!"
    image_preview3.short_description = 'image'

    def image_preview4(self,obj):
        if obj.environment_image:
            return format_html('<img src="{}" width="100" height="100" style="object-fit: cover;"/>',
                               obj.environment_image.url
                               )
        return " No image !!!"
    image_preview4.short_description = 'image'

# customize the admin display for Booking
class BookingAdmin(admin.ModelAdmin):
    list_display = ('id', 'hotel', 'user', 'check_in', 'check_out', 'status', 'created_at')
    list_filter = ('status', 'check_in', 'hotel')
    search_fields = ('user__username', 'hotel__name')
    date_hierarchy = 'check_in'

class BookingAdmin(admin.ModelAdmin):
    list_display = ('user', 'hotel', 'check_in', 'check_out', 'status')
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        
        # 1. If Superuser -> Show ALL
        if request.user.is_superuser:
            return qs
            
        # 2. If Hotel Owner -> Show ONLY bookings for their hotels
        # Find hotels owned by this user
        my_hotels = HotelDataModel.objects.filter(owner=request.user)
        # Filter booking queryset
        return qs.filter(hotel__in=my_hotels)

admin.site.register(HotelDataModel, HotelAdmin)
admin.site.register(Booking, BookingAdmin)
admin.site.register(Room)