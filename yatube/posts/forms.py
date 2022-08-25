from django import forms
from .models import Post, Comment


class PostForm(forms.ModelForm):
    text = forms.CharField(
        widget=forms.Textarea,
        label='Напишите что-нибудь',
        required=True,
        help_text='Ваше сочинение',
    )

    class Meta:
        model = Post
        fields = ('group', 'text', 'image')
        labels = {'group': 'Выберите подходящую группу'}
        help_texts = {'group': 'Группа'}


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text']
        help_texts = {'text': 'Hапишите комментарий'}
        labels = {'text': 'Комментарий'}
