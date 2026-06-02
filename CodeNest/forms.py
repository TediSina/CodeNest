from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.utils.translation import gettext_lazy as _


def _apply_form_field_classes(form):
    for field in form.fields.values():
        widget = field.widget
        existing_classes = widget.attrs.get('class', '')

        if isinstance(widget, forms.SelectMultiple):
            classes = 'form-select app-field app-field--select'
        elif isinstance(widget, forms.Select):
            classes = 'form-select app-field app-field--select'
        elif isinstance(widget, forms.Textarea):
            classes = 'form-control app-field app-field--textarea'
        else:
            classes = 'form-control app-field'

        widget.attrs['class'] = f'{existing_classes} {classes}'.strip()


class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(label=_('Email'), required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        _apply_form_field_classes(self)
        self.fields['username'].widget.attrs.setdefault('placeholder', _('Choose a username'))
        self.fields['email'].widget.attrs.setdefault('placeholder', _('Enter your email'))
        self.fields['password1'].widget.attrs.setdefault('placeholder', _('Create a password'))
        self.fields['password2'].widget.attrs.setdefault('placeholder', _('Confirm your password'))

class CustomUserChangeForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        _apply_form_field_classes(self)
        self.fields['username'].widget.attrs.setdefault('placeholder', _('Your username'))
        self.fields['email'].widget.attrs.setdefault('placeholder', _('Your email address'))
        self.fields['first_name'].widget.attrs.setdefault('placeholder', _('Your first name'))
        self.fields['last_name'].widget.attrs.setdefault('placeholder', _('Your last name'))
