"""
accounts/views.py

Handles: Registration, Login, Logout, Profile update, Dashboard routing.
Role-based redirect: students go to student dashboard, TPO to TPO dashboard.
"""

from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views import View

from .forms import StudentRegisterForm, StudentProfileForm
from .models import StudentProfile


# ─── Register ──────────────────────────────────────────────────────────────────

class RegisterView(View):
    template_name = 'accounts/register.html'

    def get(self, request):
        if request.user.is_authenticated:
            return redirect('accounts:dashboard')
        form = StudentRegisterForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = StudentRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f"Welcome {user.username}! Your account is ready.")
            return redirect('accounts:dashboard')
        return render(request, self.template_name, {'form': form})


# ─── Login ─────────────────────────────────────────────────────────────────────

class LoginView(View):
    template_name = 'accounts/login.html'

    def get(self, request):
        if request.user.is_authenticated:
            return redirect('accounts:dashboard')
        return render(request, self.template_name)

    def post(self, request):
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('accounts:dashboard')
        messages.error(request, "Invalid username or password.")
        return render(request, self.template_name)


# ─── Logout ────────────────────────────────────────────────────────────────────

def logout_view(request):
    logout(request)
    return redirect('accounts:login')


# ─── Dashboard Router ──────────────────────────────────────────────────────────

@login_required
def dashboard_view(request):
    """
    Redirects to the correct dashboard based on user role.
    """
    if request.user.is_tpo():
        return redirect('placements:tpo_dashboard')
    return redirect('placements:student_dashboard')


# ─── Student Profile ───────────────────────────────────────────────────────────

class ProfileUpdateView(View):
    template_name = 'accounts/profile.html'

    def get(self, request):
        if not request.user.is_authenticated or not request.user.is_student():
            return redirect('accounts:login')
        profile = StudentProfile.objects.get(user=request.user)
        form = StudentProfileForm(instance=profile)
        return render(request, self.template_name, {'form': form, 'profile': profile})

    def post(self, request):
        profile = StudentProfile.objects.get(user=request.user)
        form = StudentProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully!")
            return redirect('accounts:profile')
        return render(request, self.template_name, {'form': form, 'profile': profile})
