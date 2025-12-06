from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from .models import UserProfile

class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'class': 'form-control'}))
    role = forms.ChoiceField(choices=[
        ('', 'Выберите роль'),
        ('student', 'Студент'),
        ('teacher', 'Преподаватель'),
        ('other', 'Другое')
    ], required=True, widget=forms.Select(attrs={'class': 'form-select'}))
    department = forms.CharField(max_length=100, required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2', 'role', 'department']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
            profile = user.userprofile
            profile.role = self.cleaned_data['role']
            profile.department = self.cleaned_data.get('department', '')
            profile.save()
        return user

class LoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))

class ProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['avatar', 'bio', 'role', 'department']
        widgets = {
            'bio': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'role': forms.Select(attrs={'class': 'form-select'}, choices=[
                ('student', 'Студент'),
                ('teacher', 'Преподаватель'),
                ('other', 'Другое')
            ]),
            'department': forms.TextInput(attrs={'class': 'form-control'}),
        }