"""
Root URL configuration for CampusPlacementTracker.
"""

from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),
    # Redirect root to login page
    path('', RedirectView.as_view(url='/accounts/login/', permanent=False)),
    # Accounts: login, register, profile, dashboard
    path('accounts/', include('accounts.urls')),
    # Placements: drives, applications, TPO actions
    path('placements/', include('placements.urls')),
]
