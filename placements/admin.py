"""
placements/admin.py
"""

from django.contrib import admin
from .models import Company, Drive, Application


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ('name', 'website')
    search_fields = ('name',)


@admin.register(Drive)
class DriveAdmin(admin.ModelAdmin):
    list_display = ('company', 'role', 'package', 'drive_date', 'status', 'min_cgpa')
    list_filter = ('status', 'drive_date')
    search_fields = ('role', 'company__name')


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ('student', 'drive', 'status', 'applied_at')
    list_filter = ('status',)
    search_fields = ('student__full_name', 'drive__role')
