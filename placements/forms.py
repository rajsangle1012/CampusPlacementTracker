"""
placements/forms.py

Forms for TPO to create/edit drives and filter students.
"""

from django import forms
from .models import Drive, Company, Application


class CompanyForm(forms.ModelForm):
    class Meta:
        model = Company
        fields = ['name', 'description', 'website', 'logo_url']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'website': forms.URLInput(attrs={'placeholder': 'https://company.com'}),
        }


class DriveForm(forms.ModelForm):
    class Meta:
        model = Drive
        fields = [
            'company', 'role', 'package', 'drive_date',
            'location', 'description', 'min_cgpa',
            'eligible_branches', 'status'
        ]
        widgets = {
            'drive_date': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 3}),
            'eligible_branches': forms.TextInput(attrs={'placeholder': 'CSE,IT,ECE'}),
        }


class ApplicationStatusForm(forms.ModelForm):
    """TPO uses this to update an application status and add remarks."""
    class Meta:
        model = Application
        fields = ['status', 'tpo_remarks']
        widgets = {
            'tpo_remarks': forms.Textarea(attrs={'rows': 2}),
        }


class StudentFilterForm(forms.Form):
    """TPO uses this to filter students when shortlisting."""
    BRANCH_CHOICES = [('', 'All Branches')] + [
        ('CSE', 'CSE'), ('IT', 'IT'), ('ECE', 'ECE'),
        ('ME', 'ME'), ('CE', 'CE'), ('EE', 'EE'),
    ]
    branch = forms.ChoiceField(choices=BRANCH_CHOICES, required=False)
    min_cgpa = forms.DecimalField(max_digits=4, decimal_places=2, required=False,
                                  initial=6.0, label="Min CGPA")
    is_placed = forms.ChoiceField(
        choices=[('', 'All'), ('False', 'Unplaced'), ('True', 'Placed')],
        required=False, label="Placement Status"
    )
