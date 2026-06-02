import re

from django import forms
from django.utils.translation import gettext_lazy as _

from .models import Answer, Comment, Question, Tag


def _add_widget_classes(field, classes, placeholder=None):
    field.widget.attrs["class"] = classes
    if placeholder:
        field.widget.attrs["placeholder"] = placeholder


class QuestionForm(forms.ModelForm):
    tags = forms.CharField(
        label=_('Tags'),
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control app-field',
            'placeholder': 'python, django, javascript',
        }),
        help_text=_('Add tags separated by commas. New tags are created automatically.'),
    )

    class Meta:
        model = Question
        fields = ['title', 'body', 'tags']
        labels = {
            'title': _('Title'),
            'body': _('Details'),
        }
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control app-field',
                'placeholder': _('Enter your question title')
            }),
            'body': forms.Textarea(attrs={
                'class': 'form-control app-field app-field--textarea markdown-input',
                'rows': 18,
                'placeholder': _('Write your question using Markdown')
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        _add_widget_classes(self.fields['title'], 'form-control app-field', _('Summarize the problem in one clear sentence'))
        _add_widget_classes(self.fields['body'], 'form-control app-field app-field--textarea markdown-input', _('Add context, the code you tried, and the result you expected'))
        _add_widget_classes(self.fields['tags'], 'form-control app-field', 'python, django, javascript')

        if self.instance.pk:
            self.initial['tags'] = ', '.join(
                self.instance.tags.values_list('name', flat=True)
            )

    def clean_tags(self):
        tag_names = []
        seen_names = set()
        max_length = Tag._meta.get_field('name').max_length

        for raw_name in re.split(r'[,\n]+', self.cleaned_data['tags']):
            name = raw_name.strip().lstrip('#').strip().lower()

            if not name or name in seen_names:
                continue

            if len(name) > max_length:
                raise forms.ValidationError(
                    _('Tags must be %(max_length)s characters or fewer.')
                    % {'max_length': max_length}
                )

            tag_names.append(name)
            seen_names.add(name)

        return tag_names

    def _save_m2m(self):
        tags = []

        for name in self.cleaned_data['tags']:
            tag = Tag.objects.filter(name__iexact=name).order_by('pk').first()

            if tag is None:
                tag, _ = Tag.objects.get_or_create(name=name)

            tags.append(tag)

        self.instance.tags.set(tags)

class AnswerForm(forms.ModelForm):
    class Meta:
        model = Answer
        fields = ['body']
        labels = {
            'body': _('Answer'),
        }
        widgets = {
            'body': forms.Textarea(attrs={
                'class': 'form-control app-field app-field--textarea markdown-input',
                'rows': 16,
                'placeholder': _('Write your answer using Markdown')
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        _add_widget_classes(
            self.fields['body'],
            'form-control app-field app-field--textarea markdown-input',
            _('Share the fix, why it works, and any caveats someone should know')
        )


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']
        labels = {
            'content': _('Comment'),
        }
        widgets = {
            'content': forms.Textarea(attrs={
                'rows': 2,
                'placeholder': _('Add a comment'),
            }),
        }
