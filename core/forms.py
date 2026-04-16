from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, Post, Message  # ← важно: своя модель


class UserRegistrationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'password1', 'password2']


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['text']
        widgets = {
            'text': forms.Textarea(attrs={
                'rows': 4,
                'placeholder': 'Что нового?',
                'style': 'width: 100%; background: #2a2a2a; color: #e0e0e0; border: 1px solid #444; border-radius: 8px; padding: 12px;'
            }),
        }


class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ['text']
        widgets = {
            'text': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': 'Напишите сообщение...',
                'style': 'width: 100%; background: #2a2a2a; color: #e0e0e0; border: 1px solid #444; border-radius: 8px; padding: 12px;'
            }),
        }