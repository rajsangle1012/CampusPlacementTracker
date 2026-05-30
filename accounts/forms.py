"""
accounts/forms.py

Registration and profile update forms.
"""

from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, StudentProfile


class StudentRegisterForm(UserCreationForm):
    """
    Combines User creation with StudentProfile fields.
    TPO accounts are created via Django admin only (for security).
    """
    email = forms.EmailField(required=True)
    full_name = forms.CharField(max_length=100)
    roll_number = forms.CharField(max_length=20)
    branch = forms.ChoiceField(choices=StudentProfile.BRANCH_CHOICES)
    cgpa = forms.DecimalField(max_digits=4, decimal_places=2)
    graduation_year = forms.IntegerField(initial=2025)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    def save(self, commit=True):
        # Save User with role = student
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.role = User.STUDENT
        if commit:
            user.save()
            # Create linked StudentProfile
            StudentProfile.objects.create(
                user=user,
                full_name=self.cleaned_data['full_name'],
                roll_number=self.cleaned_data['roll_number'],
                branch=self.cleaned_data['branch'],
                cgpa=self.cleaned_data['cgpa'],
                graduation_year=self.cleaned_data['graduation_year'],
            )
        return user


class StudentProfileForm(forms.ModelForm):
    """Allows students to update their profile after registration."""
    class Meta:
        model = StudentProfile
        fields = ['full_name', 'branch', 'cgpa', 'skills', 'resume_link', 'phone', 'graduation_year']
        widgets = {
            'skills': forms.TextInput(attrs={'placeholder': 'Python, Django, SQL ...'}),
            'resume_link': forms.URLInput(attrs={'placeholder': 'https://drive.google.com/...'}),
        }
