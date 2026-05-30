"""
placements/urls.py
"""

from django.urls import path
from . import views

app_name = 'placements'

urlpatterns = [
    # ── Student URLs ─────────────────────────────────────────────────────
    path('dashboard/', views.StudentDashboardView.as_view(), name='student_dashboard'),
    path('apply/<int:drive_id>/', views.apply_drive_view, name='apply_drive'),
    path('my-applications/', views.StudentApplicationsView.as_view(), name='my_applications'),

    # ── TPO URLs ──────────────────────────────────────────────────────────
    path('tpo/', views.TPODashboardView.as_view(), name='tpo_dashboard'),
    path('tpo/drives/', views.DriveListView.as_view(), name='drive_list'),
    path('tpo/drives/new/', views.DriveCreateView.as_view(), name='drive_create'),
    path('tpo/companies/new/', views.CompanyCreateView.as_view(), name='company_create'),
    path('tpo/drives/<int:drive_id>/edit/', views.DriveUpdateView.as_view(), name='drive_edit'),
    path('tpo/drives/<int:drive_id>/delete/', views.drive_delete_view, name='drive_delete'),
    path('tpo/drives/<int:drive_id>/applicants/', views.DriveApplicantsView.as_view(), name='drive_applicants'),
    path('tpo/applications/<int:app_id>/update/', views.update_application_view, name='update_application'),
    path('tpo/students/', views.StudentListView.as_view(), name='student_list'),
]
