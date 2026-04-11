from django import forms
from .models import Question, Answer, Comment


def _add_widget_classes(field, classes, placeholder=None):
    field.widget.attrs["class"] = classes
    if placeholder:
        field.widget.attrs["placeholder"] = placeholder


class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['title', 'body', 'tags']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control app-field',
                'placeholder': 'Enter your question title'
            }),
            'body': forms.Textarea(attrs={
                'class': 'form-control app-field app-field--textarea markdown-input',
                'rows': 18,
                'placeholder': 'Write your question using Markdown'
            }),
            'tags': forms.SelectMultiple(attrs={
                'class': 'form-select app-field app-field--select',
                'size': 6,
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        _add_widget_classes(self.fields['title'], 'form-control app-field', 'Summarize the problem in one clear sentence')
        _add_widget_classes(self.fields['body'], 'form-control app-field app-field--textarea markdown-input', 'Add context, the code you tried, and the result you expected')
        _add_widget_classes(self.fields['tags'], 'form-select app-field app-field--select')
        self.fields['tags'].help_text = 'Hold Ctrl (or Cmd on Mac) to select multiple tags.'

class AnswerForm(forms.ModelForm):
    class Meta:
        model = Answer
        fields = ['body']
        widgets = {
            'body': forms.Textarea(attrs={
                'class': 'form-control app-field app-field--textarea markdown-input',
                'rows': 16,
                'placeholder': 'Write your answer using Markdown'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        _add_widget_classes(
            self.fields['body'],
            'form-control app-field app-field--textarea markdown-input',
            'Share the fix, why it works, and any caveats someone should know'
        )
