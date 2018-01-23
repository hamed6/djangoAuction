from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm


class createAuctionForm(UserCreationForm):
    # Email = forms.EmailField(required=True)
    # userName=forms.CharField(required=True)
    # userPassword=forms.CharField(required=True)
    class Meta:
        model=User
        fields=('username','password1' ,'password2','email')


class confirmationForm(forms.Form):
    CHOICES = [(x, x) for x in ("Yes", "No")]
    Option = forms.ChoiceField(choices=CHOICES)

class dropDown(forms.Form):
    dropRange=forms.ChoiceField(choices=[(x, x) for x in range(1, 32)])
