"""
placements/models.py

Three core models:
  - Company   : company info
  - Drive     : a placement drive posted by TPO (linked to Company)
  - Application: a student applying to a Drive
"""

from django.db import models
from accounts.models import StudentProfile


class Company(models.Model):
    """Stores company details added by TPO."""
    name = models.CharField(max_length=150)
    description = models.TextField(blank=True)
    website = models.URLField(blank=True)
    logo_url = models.URLField(blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'Companies'


class Drive(models.Model):
    """
    A company drive (campus recruitment event).
    TPO creates, edits, deletes drives.
    Students filter and apply.
    """
    STATUS_OPEN = 'open'
    STATUS_CLOSED = 'closed'
    STATUS_CHOICES = [
        (STATUS_OPEN, 'Open'),
        (STATUS_CLOSED, 'Closed'),
    ]

    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='drives')
    role = models.CharField(max_length=150, help_text="Job role, e.g. Software Engineer")
    package = models.CharField(max_length=50, help_text="e.g. 6 LPA")
    drive_date = models.DateField()
    location = models.CharField(max_length=100, blank=True)
    description = models.TextField(blank=True)

    # Eligibility filters
    min_cgpa = models.DecimalField(max_digits=4, decimal_places=2, default=6.00)
    eligible_branches = models.CharField(
        max_length=255,
        help_text="Comma-separated branch codes, e.g. CSE,IT,ECE",
        default='CSE,IT,ECE,ME,CE,EE'
    )

    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=STATUS_OPEN)
    created_at = models.DateTimeField(auto_now_add=True)

    def branch_list(self):
        """Returns list of eligible branches from CSV string."""
        return [b.strip() for b in self.eligible_branches.split(',')]

    def is_student_eligible(self, profile):
        """Check if a StudentProfile meets eligibility."""
        return (
            profile.cgpa >= self.min_cgpa and
            profile.branch in self.branch_list()
        )

    def __str__(self):
        return f"{self.company.name} – {self.role} ({self.drive_date})"


class Application(models.Model):
    """
    Tracks a student's application to a specific drive.
    Status flows: Applied → Shortlisted → Selected / Rejected
    """
    STATUS_APPLIED = 'applied'
    STATUS_SHORTLISTED = 'shortlisted'
    STATUS_SELECTED = 'selected'
    STATUS_REJECTED = 'rejected'

    STATUS_CHOICES = [
        (STATUS_APPLIED, 'Applied'),
        (STATUS_SHORTLISTED, 'Shortlisted'),
        (STATUS_SELECTED, 'Selected'),
        (STATUS_REJECTED, 'Rejected'),
    ]

    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='applications')
    drive = models.ForeignKey(Drive, on_delete=models.CASCADE, related_name='applications')
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default=STATUS_APPLIED)
    applied_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    tpo_remarks = models.TextField(blank=True, help_text="Internal remarks by TPO")

    class Meta:
        # A student cannot apply to the same drive twice
        unique_together = ('student', 'drive')
        ordering = ['-applied_at']

    def __str__(self):
        return f"{self.student.full_name} → {self.drive} [{self.status}]"
