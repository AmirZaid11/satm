from django import forms
from django.contrib.auth.forms import PasswordChangeForm, UserCreationForm as BaseUserCreationForm, UserChangeForm as BaseUserChangeForm
from .models import User
from django.utils.translation import gettext_lazy as _

class CustomUserCreationForm(BaseUserCreationForm):
    role = forms.ChoiceField(choices=User.ROLE_CHOICES, required=True)
    
    class Meta(BaseUserCreationForm.Meta):
        model = User
        fields = ("username", "role", "course")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make password optional if role is student
        # Note: BaseUserCreationForm has password1 and password2 fields
        # However, validation is handled in clean(). 
        # For simplicity, we just make them not required in the form if we can detect the role,
        # but role is selected in the same form. 
        # So we handle it in clean()
        pass

    def clean(self):
        cleaned_data = super().clean()
        role = cleaned_data.get("role")
        if role == 'student':
            # Remove password errors if role is student
            if 'password1' in self._errors:
                del self._errors['password1']
            if 'password2' in self._errors:
                del self._errors['password2']
            
            # Ensure password1 is in cleaned_data to avoid KeyError in parent save()
            if 'password1' not in cleaned_data or not cleaned_data['password1']:
                cleaned_data['password1'] = cleaned_data.get('username')
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        role = self.cleaned_data.get("role")
        if role:
            user.role = role
        if role == 'student':
            user.set_password(user.username)
            user.must_change_password = False
        if commit:
            user.save()
        return user

class CustomUserChangeForm(BaseUserChangeForm):
    class Meta(BaseUserChangeForm.Meta):
        model = User

class StudentProfileForm(forms.ModelForm):
    year = forms.ChoiceField(choices=[(1, 'Year 1'), (2, 'Year 2'), (3, 'Year 3'), (4, 'Year 4')], widget=forms.Select(attrs={
        'class': 'w-full px-4 py-3 rounded-xl border border-slate-200 focus:ring-2 focus:ring-sky-500 focus:border-sky-500 outline-none transition bg-slate-50'
    }))
    semester = forms.ChoiceField(choices=[(1, 'Semester 1'), (2, 'Semester 2')], widget=forms.Select(attrs={
        'class': 'w-full px-4 py-3 rounded-xl border border-slate-200 focus:ring-2 focus:ring-sky-500 focus:border-sky-500 outline-none transition bg-slate-50'
    }))

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'profile_picture', 'year', 'semester']
        labels = {
            'first_name': 'First Name',
            'last_name': 'Last Name',
            'email': 'Email Address',
            'profile_picture': 'Profile Photo',
            'year': 'Year of Study',
            'semester': 'Current Semester',
        }
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 rounded-xl border border-slate-200 focus:ring-2 focus:ring-sky-500 focus:border-sky-500 outline-none transition bg-slate-50',
                'placeholder': 'Enter your first name'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 rounded-xl border border-slate-200 focus:ring-2 focus:ring-sky-500 focus:border-sky-500 outline-none transition bg-slate-50',
                'placeholder': 'Enter your last name'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'w-full px-4 py-3 rounded-xl border border-slate-200 focus:ring-2 focus:ring-sky-500 focus:border-sky-500 outline-none transition bg-slate-50',
                'placeholder': 'Enter your email'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['profile_picture'].widget.attrs.update({
            'class': 'block w-full text-sm text-slate-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-sky-50 file:text-sky-700 hover:file:bg-sky-100 transition'
        })
