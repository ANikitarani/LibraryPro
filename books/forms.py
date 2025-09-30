from django import forms

class ReservationForm(forms.Form):
    contact_name = forms.CharField(max_length=100, required=False, widget=forms.TextInput(attrs={'placeholder': 'Your Name'}))
    contact_email = forms.EmailField(required=False, widget=forms.EmailInput(attrs={'placeholder': 'Your Email'}))
