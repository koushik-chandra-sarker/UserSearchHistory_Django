from django import forms
from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q

User = get_user_model()


class UserRegistrationForm(forms.ModelForm):
    username = forms.CharField(
        required=True,
        widget=forms.TextInput(
            attrs={
                'class': 'form_control',
                'type': 'text',
                'placeholder': 'Username'
            }
        )
    )
    password1 = forms.CharField(
        required=True,
        widget=forms.TextInput(
            attrs={
                'class': 'form_control',
                'id': 'password1',
                'type': 'password',
                'placeholder': 'Password'
            }
        )
    )
    password2 = forms.CharField(
        required=True,
        widget=forms.TextInput(
            attrs={
                'class': 'form_control',
                'id': 'password2',
                'type': 'password',
                'placeholder': 'Confirm Password'
            }
        )
    )

    class Meta:
        model = User
        fields = ['username', 'password1', 'password2']

    def clean_password2(self):
        pass1 = self.cleaned_data.get('password1')
        pass2 = self.cleaned_data.get('password2')
        if pass1 and pass2 and pass1 != pass2:
            raise forms.ValidationError("Password doesn't match")
        return pass2

    def clean_username(self):
        error_massages = {
            'duplicate_username': 'User with this username already taken.'

        }
        username = self.cleaned_data.get('username')
        try:
            User.objects.get(username=username)
            raise forms.ValidationError(
                error_massages['duplicate_username'],
                code='duplicate_username'
            )
        except ObjectDoesNotExist:
            return username

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data.get('password1'))
        if commit:
            user.save()

        return user


class UserLoginForm(forms.Form):
    username = forms.CharField(
        required=True,
        widget=forms.TextInput(
            attrs={
                'class': 'form_control',
                'type': 'text',
                'id': 'username',
                'placeholder': 'Username'
            }
        )
    )
    password = forms.CharField(
        required=True,
        widget=forms.TextInput(
            attrs={
                'class': 'form_control',
                'id': 'password',
                'type': 'password',
                'placeholder': 'Password'
            }
        )
    )

    # def clean_username(self):
    #     username = self.cleaned_data.get('username')
    #     try:
    #         user = User.objects.filter(Q(username__iexact=username)).distinct()
    #         if not user.exists() and user.count != 1:
    #             raise forms.ValidationError('User dose not exist.', code='username_error')
    #         # user = user.first()
    #     except ObjectDoesNotExist:
    #         return username

    # def clean_password(self):
    #     username = self.cleaned_data.get('username')
    #     password = self.cleaned_data.get('password')
    #     print(username)
    #     if username is None:
    #         raise forms.ValidationError('Bad credentials', code='password_error')
    #     return password

    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')
        try:
            user = User.objects.filter(Q(username__iexact=username)).distinct()
            if not user.exists() and user.count != 1:
                raise forms.ValidationError('User dose not exist.', code='username_error')
            user = user.first()
            if not (user.check_password(password)):
                raise forms.ValidationError('Bad credentials', code='password_error')
        except ObjectDoesNotExist:
            return username
        self.cleaned_data['user'] = user
        return super(UserLoginForm, self).clean()
