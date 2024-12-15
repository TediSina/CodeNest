from django import forms
from .models import Question, Answer, Comment

class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['title', 'body', 'tags']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control bg-dark text-light border-secondary', 
                'placeholder': 'Enter your question title'
            }),
            'body': forms.Textarea(attrs={
                'class': 'form-control bg-dark text-light border-secondary markdown-input', 
                'rows': 20, 
                'placeholder': 'Write your question using Markdown'
            }),
            'tags': forms.SelectMultiple(attrs={
                'class': 'form-control bg-dark text-light border-secondary'
            }),
        }

class AnswerForm(forms.ModelForm):
    class Meta:
        model = Answer
        fields = ['body']
        widgets = {
            'body': forms.Textarea(attrs={
                'class': 'form-control bg-dark text-light border-secondary markdown-input',
                'rows': 5, 
                'placeholder': 'Write your answer using Markdown'
            }),
        }
