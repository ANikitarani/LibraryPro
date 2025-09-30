from django import forms
from .models import Reservation

class ReservationForm(forms.ModelForm):
    contact_name = forms.CharField(
        max_length=100,
        required=True,
        label='Your Name (for notifications)',
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    contact_email = forms.EmailField(
        required=True,
        label='Email for Notifications',
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = Reservation
        fields = ['contact_name', 'contact_email']
        widgets = {
            'contact_name': forms.TextInput(attrs={'class': 'form-control'}),
            'contact_email': forms.EmailInput(attrs={'class': 'form-control'}),
        }
