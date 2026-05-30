"""
placements/views.py

Student Views:
  - StudentDashboardView   : shows drives the student is eligible for
  - ApplyDriveView         : apply to a drive
  - StudentApplicationsView: track own applications

TPO Views:
  - TPODashboardView       : stats overview
  - DriveListView          : list all drives
  - DriveCreateView        : add a new drive
  - DriveUpdateView        : edit a drive
  - DriveDeleteView        : delete a drive
  - DriveApplicantsView    : see all applicants for a drive
  - UpdateApplicationView  : change application status
  - StudentListView        : list students with filters
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views import View
from django.contrib import messages
from django.db.models import Count, Q

from accounts.models import StudentProfile
from .models import Company, Drive, Application
from .forms import DriveForm, CompanyForm, ApplicationStatusForm, StudentFilterForm


# ─── Decorators / helpers ──────────────────────────────────────────────────────

def student_required(view_func):
    """Decorator: only students can access."""
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.is_student():
            return redirect('accounts:login')
        return view_func(request, *args, **kwargs)
    return wrapper


def tpo_required(view_func):
    """Decorator: only TPO can access."""
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.is_tpo():
            return redirect('accounts:login')
        return view_func(request, *args, **kwargs)
    return wrapper


# ══════════════════════════════════════════════════════════════════════════════
# STUDENT VIEWS
# ══════════════════════════════════════════════════════════════════════════════

class StudentDashboardView(View):
    """
    Student landing page.
    Shows: stats, list of open drives filtered by eligibility.
    """
    template_name = 'placements/student_dashboard.html'

    @method_decorator(login_required)
    def get(self, request):
        if not request.user.is_student():
            return redirect('accounts:login')

        profile = get_object_or_404(StudentProfile, user=request.user)
        open_drives = Drive.objects.filter(status=Drive.STATUS_OPEN).select_related('company')

        # Only show drives the student is eligible for
        eligible_drives = [d for d in open_drives if d.is_student_eligible(profile)]

        # IDs of drives student already applied to
        applied_ids = Application.objects.filter(
            student=profile
        ).values_list('drive_id', flat=True)

        # Application stats
        my_apps = Application.objects.filter(student=profile)
        stats = {
            'total': my_apps.count(),
            'shortlisted': my_apps.filter(status=Application.STATUS_SHORTLISTED).count(),
            'selected': my_apps.filter(status=Application.STATUS_SELECTED).count(),
        }

        context = {
            'profile': profile,
            'eligible_drives': eligible_drives,
            'applied_ids': list(applied_ids),
            'stats': stats,
        }
        return render(request, self.template_name, context)


@student_required
@login_required
def apply_drive_view(request, drive_id):
    """Student applies to a drive."""
    profile = get_object_or_404(StudentProfile, user=request.user)
    drive = get_object_or_404(Drive, id=drive_id)

    if drive.status != Drive.STATUS_OPEN:
        messages.error(request, "This drive is no longer accepting applications.")
        return redirect('placements:student_dashboard')

    if not drive.is_student_eligible(profile):
        messages.error(request, "You do not meet the eligibility criteria for this drive.")
        return redirect('placements:student_dashboard')

    # Prevent duplicate application
    if Application.objects.filter(student=profile, drive=drive).exists():
        messages.warning(request, "You have already applied for this drive.")
        return redirect('placements:my_applications')

    Application.objects.create(student=profile, drive=drive)
    messages.success(request, f"Successfully applied to {drive.company.name} – {drive.role}!")
    return redirect('placements:my_applications')


class StudentApplicationsView(View):
    """Student tracks all their applications and statuses."""
    template_name = 'placements/my_applications.html'

    @method_decorator(login_required)
    def get(self, request):
        if not request.user.is_student():
            return redirect('accounts:login')
        profile = get_object_or_404(StudentProfile, user=request.user)
        applications = Application.objects.filter(
            student=profile
        ).select_related('drive__company')
        return render(request, self.template_name, {'applications': applications, 'profile': profile})


# ══════════════════════════════════════════════════════════════════════════════
# TPO VIEWS
# ══════════════════════════════════════════════════════════════════════════════

class TPODashboardView(View):
    """TPO overview: stats, recent drives, placement summary."""
    template_name = 'placements/tpo_dashboard.html'

    @method_decorator(login_required)
    def get(self, request):
        if not request.user.is_tpo():
            return redirect('accounts:login')

        stats = {
            'total_students': StudentProfile.objects.count(),
            'placed_students': StudentProfile.objects.filter(is_placed=True).count(),
            'total_drives': Drive.objects.count(),
            'open_drives': Drive.objects.filter(status=Drive.STATUS_OPEN).count(),
            'total_applications': Application.objects.count(),
            'selected_applications': Application.objects.filter(status=Application.STATUS_SELECTED).count(),
        }

        recent_drives = Drive.objects.all().select_related('company').order_by('-created_at')[:5]

        # Branch-wise placement counts for a simple table
        branch_data = StudentProfile.objects.values('branch').annotate(
            total=Count('id'),
            placed=Count('id', filter=Q(is_placed=True))
        )

        context = {
            'stats': stats,
            'recent_drives': recent_drives,
            'branch_data': branch_data,
        }
        return render(request, self.template_name, context)


class DriveListView(View):
    template_name = 'placements/drive_list.html'

    @method_decorator(login_required)
    def get(self, request):
        if not request.user.is_tpo():
            return redirect('accounts:login')
        drives = Drive.objects.all().select_related('company').order_by('-created_at')
        return render(request, self.template_name, {'drives': drives})


class DriveCreateView(View):
    template_name = 'placements/drive_form.html'

    @method_decorator(login_required)
    def get(self, request):
        if not request.user.is_tpo():
            return redirect('accounts:login')
        return render(request, self.template_name, {
            'form': DriveForm(),
            'company_form': CompanyForm(),
            'title': 'Add New Drive'
        })

    @method_decorator(login_required)
    def post(self, request):
        form = DriveForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Drive created successfully!")
            return redirect('placements:drive_list')
        return render(request, self.template_name, {
            'form': form,
            'company_form': CompanyForm(),
            'title': 'Add New Drive'
        })


class CompanyCreateView(View):
    template_name = 'placements/company_form.html'

    @method_decorator(login_required)
    def get(self, request):
        if not request.user.is_tpo():
            return redirect('accounts:login')
        return render(request, self.template_name, {
            'form': CompanyForm(),
            'title': 'Add New Company'
        })

    @method_decorator(login_required)
    def post(self, request):
        if not request.user.is_tpo():
            return redirect('accounts:login')
        form = CompanyForm(request.POST)
        if form.is_valid():
            company = form.save()
            messages.success(request, f"Company '{company.name}' added successfully!")
            return redirect('placements:tpo_dashboard')
        return render(request, self.template_name, {
            'form': form,
            'title': 'Add New Company'
        })


class DriveUpdateView(View):
    template_name = 'placements/drive_form.html'

    @method_decorator(login_required)
    def get(self, request, drive_id):
        if not request.user.is_tpo():
            return redirect('accounts:login')
        drive = get_object_or_404(Drive, id=drive_id)
        return render(request, self.template_name, {
            'form': DriveForm(instance=drive),
            'title': f'Edit Drive – {drive}'
        })

    @method_decorator(login_required)
    def post(self, request, drive_id):
        drive = get_object_or_404(Drive, id=drive_id)
        form = DriveForm(request.POST, instance=drive)
        if form.is_valid():
            form.save()
            messages.success(request, "Drive updated successfully!")
            return redirect('placements:drive_list')
        return render(request, self.template_name, {
            'form': form,
            'title': f'Edit Drive – {drive}'
        })


@tpo_required
@login_required
def drive_delete_view(request, drive_id):
    drive = get_object_or_404(Drive, id=drive_id)
    if request.method == 'POST':
        drive.delete()
        messages.success(request, "Drive deleted.")
        return redirect('placements:drive_list')
    return render(request, 'placements/confirm_delete.html', {'obj': drive})


class DriveApplicantsView(View):
    """TPO sees all applicants for a specific drive, with filter option."""
    template_name = 'placements/drive_applicants.html'

    @method_decorator(login_required)
    def get(self, request, drive_id):
        if not request.user.is_tpo():
            return redirect('accounts:login')
        drive = get_object_or_404(Drive, id=drive_id)
        applications = Application.objects.filter(
            drive=drive
        ).select_related('student').order_by('status')
        return render(request, self.template_name, {
            'drive': drive,
            'applications': applications
        })


@tpo_required
@login_required
def update_application_view(request, app_id):
    """TPO updates application status (shortlist / select / reject)."""
    application = get_object_or_404(Application, id=app_id)
    if request.method == 'POST':
        form = ApplicationStatusForm(request.POST, instance=application)
        if form.is_valid():
            app = form.save()
            # Auto-mark student as placed if Selected
            if app.status == Application.STATUS_SELECTED:
                app.student.is_placed = True
                app.student.save()
            messages.success(request, "Application status updated.")
            return redirect('placements:drive_applicants', drive_id=application.drive.id)
    else:
        form = ApplicationStatusForm(instance=application)
    return render(request, 'placements/update_application.html', {
        'form': form,
        'application': application
    })


class StudentListView(View):
    """TPO views all students with branch/CGPA filters for shortlisting."""
    template_name = 'placements/student_list.html'

    @method_decorator(login_required)
    def get(self, request):
        if not request.user.is_tpo():
            return redirect('accounts:login')

        filter_form = StudentFilterForm(request.GET or None)
        students = StudentProfile.objects.all()

        if filter_form.is_valid():
            branch = filter_form.cleaned_data.get('branch')
            min_cgpa = filter_form.cleaned_data.get('min_cgpa')
            is_placed = filter_form.cleaned_data.get('is_placed')

            if branch:
                students = students.filter(branch=branch)
            if min_cgpa:
                students = students.filter(cgpa__gte=min_cgpa)
            if is_placed in ('True', 'False'):
                students = students.filter(is_placed=(is_placed == 'True'))

        return render(request, self.template_name, {
            'students': students,
            'filter_form': filter_form
        })
