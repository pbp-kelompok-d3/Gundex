from django.forms import ModelForm, CharField, PasswordInput, BooleanField
from django.core.exceptions import ValidationError
from django.utils.html import strip_tags
from .models import UserProfile

class RegisterForm(ModelForm):
    password = CharField(widget=PasswordInput())
    confirm_password = CharField(widget=PasswordInput())
    register_as_admin = BooleanField(required=False, label="Register as Admin")
    
    class Meta:
        model = UserProfile
        fields = ['username', 'email', 'first_name', 'last_name', 'bio']
    
    def clean_username(self):
        username = self.cleaned_data["username"]
        return strip_tags(username)
    
    def clean_first_name(self):
        first_name = self.cleaned_data["first_name"]
        return strip_tags(first_name)
    
    def clean_last_name(self):
        last_name = self.cleaned_data["last_name"]
        return strip_tags(last_name)
    
    def clean_bio(self):
        bio = self.cleaned_data["bio"]
        return strip_tags(bio) if bio else bio
    
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")
        
        if password and confirm_password and password != confirm_password:
            raise ValidationError("Passwords don't match")
        
        return cleaned_data

class EditProfileForm(ModelForm):
    class Meta:
        model = UserProfile
        fields = ['username', 'bio']
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
    
    def clean_username(self):
        username = self.cleaned_data["username"]
        return strip_tags(username)
    
    def clean_bio(self):
        bio = self.cleaned_data["bio"]
        return strip_tags(bio) if bio else bio