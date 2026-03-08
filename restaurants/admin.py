from django.contrib import admin
from .models import RestaurantDataModel, TableReservation


@admin.register(RestaurantDataModel)
class RestaurantAdmin(admin.ModelAdmin):
    list_display = ['name', 'city', 'area', 'badge', 'cuisine_type', 'price_range', 'rating', 'total_tables']
    list_filter = ['badge', 'city', 'price_range', 'cuisine_type']
    search_fields = ['name', 'city', 'area', 'description']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('owner', 'name', 'city', 'area', 'badge', 'cuisine_type', 'price_range')
        }),
        ('Pricing & Capacity', {
            'fields': ('average_cost_for_two', 'total_tables')
        }),
        ('Details', {
            'fields': ('description', 'rating')
        }),
        ('Images', {
            'fields': ('image', 'menu_image', 'interior_image')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(TableReservation)
class TableReservationAdmin(admin.ModelAdmin):
    list_display = ['user', 'restaurant', 'reservation_date', 'reservation_time', 'number_of_guests', 'tables_reserved', 'status', 'created_at']
    list_filter = ['status', 'reservation_date', 'restaurant']
    search_fields = ['user__email', 'user__first_name', 'user__last_name', 'restaurant__name']
    readonly_fields = ['created_at', 'tables_reserved']
    date_hierarchy = 'reservation_date'
    
    fieldsets = (
        ('Reservation Details', {
            'fields': ('user', 'restaurant', 'reservation_date', 'reservation_time')
        }),
        ('Guest Information', {
            'fields': ('number_of_guests', 'tables_reserved', 'special_requests')
        }),
        ('Status', {
            'fields': ('status', 'created_at')
        }),
    )
