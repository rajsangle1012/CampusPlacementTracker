"""
accounts/models.py

Custom User model with a role field (STUDENT / TPO).
StudentProfile stores placement-relevant fields.
"""

from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    Extends Django's built-in User.
    Adds a role so we can distinguish Students from TPO officers.
    """
    STUDENT = 'student'
    TPO = 'tpo'
    ROLE_CHOICES = [
        (STUDENT, 'Student'),
        (TPO, 'TPO'),
    ]
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default=STUDENT)
    email = models.EmailField(unique=True)

    def is_student(self):
        return self.role == self.STUDENT

    def is_tpo(self):
        return self.role == self.TPO

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"


class StudentProfile(models.Model):
    """
    One-to-one extension of the User model for students.
    Stores academic and contact details needed for placement filtering.
    """
    BRANCH_CHOICES = [
        ('CSE', 'Computer Science Engineering'),
        ('IT', 'Information Technology'),
        ('ECE', 'Electronics & Communication'),
        ('ME', 'Mechanical Engineering'),
        ('CE', 'Civil Engineering'),
        ('EE', 'Electrical Engineering'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student_profile')
    full_name = models.CharField(max_length=100)
    roll_number = models.CharField(max_length=20, unique=True)
    branch = models.CharField(max_length=10, choices=BRANCH_CHOICES)
    cgpa = models.DecimalField(max_digits=4, decimal_places=2, help_text="e.g. 8.75")
    skills = models.TextField(blank=True, help_text="Comma-separated skills, e.g. Python, SQL, Django")
    resume_link = models.URLField(blank=True, help_text="Google Drive or any public link to resume")
    phone = models.CharField(max_length=15, blank=True)
    graduation_year = models.PositiveIntegerField(default=2025)
    is_placed = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.full_name} ({self.roll_number})"
