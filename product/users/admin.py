from django.contrib import admin
from .models import CustomUser, Balance, Subscription

@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('email', 'first_name', 'last_name', 'is_staff')
    search_fields = ('email', 'first_name', 'last_name')
    list_filter = ('is_staff', 'is_active', 'is_superuser')

@admin.register(Balance)
class BalanceAdmin(admin.ModelAdmin):
    list_display = ('user', 'balance')
    search_fields = ('user__email',)
    list_filter = ('balance',)

@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('user', 'course', 'start_date', 'end_date', 'is_active')
    search_fields = ('user__email', 'course__title')
    list_filter = ('is_active', 'start_date', 'end_date')
