from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from django import forms

User = get_user_model()


class CreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('first_name', 'last_name', 'username', 'email')


class PasswordChangeForm(forms.Form):
    old_password = forms.CharField(label='Введите текущий пароль')
    new_password = forms.CharField(label='Введите новый пароль')
    confirm_password = forms.CharField(label='Введите новый пароль повторно')
