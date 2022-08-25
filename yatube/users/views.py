from django.views.generic import CreateView
from django.urls import reverse_lazy
from .forms import CreationForm, PasswordChangeForm


class SignUp(CreateView):
    form_class = CreationForm
    # После успешной регистрации перенаправляем пользователя на главную.
    success_url = reverse_lazy('posts:index')
    template_name = 'users/signup.html'


class PasswordChangeForm(CreateView):
    form_class = PasswordChangeForm
    success_url = 'users:password_change_done.html'
    template_name = 'users/password_change_form.hrml'
