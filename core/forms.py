from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from .models import User, Product

class SignupForm(forms.ModelForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'autocomplete': 'username'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'}))
    password_confirm = forms.CharField(widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'}), label="Confirm Password")

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'phone', 'address']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'].required = True
        self.fields['first_name'].required = True
        self.fields['last_name'].required = True

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        password_confirm = cleaned_data.get("password_confirm")

        if password and password_confirm:
            if password != password_confirm:
                self.add_error('password_confirm', "Passwords do not match")
            
            # Validate password strength using Django's built-in validators
            try:
                validate_password(password, self.instance)
            except ValidationError as e:
                self.add_error('password', e)
                
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'category', 'description', 'price', 'stock_quantity', 'image', 'is_active']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }

class CheckoutForm(forms.Form):
    delivery_address = forms.CharField(widget=forms.Textarea(attrs={'rows': 3}))
    payment_method = forms.ChoiceField(choices=[('CASH', 'Cash on Delivery'), ('CARD', 'Credit/Debit Card')])
    
    # Card details (will be shown/hidden via JS)
    card_name = forms.CharField(required=False, label="Cardholder Name")
    card_number = forms.CharField(required=False, label="Card Number", max_length=16)
    card_expiry = forms.CharField(required=False, label="Expiry Date (MM/YY)", max_length=5)
    card_cvv = forms.CharField(required=False, label="CVV", max_length=4)

    def clean(self):
        cleaned_data = super().clean()
        payment_method = cleaned_data.get('payment_method')
        
        if payment_method == 'CARD':
            card_name = cleaned_data.get('card_name')
            card_number = cleaned_data.get('card_number')
            card_expiry = cleaned_data.get('card_expiry')
            card_cvv = cleaned_data.get('card_cvv')
            
            if not all([card_name, card_number, card_expiry, card_cvv]):
                raise forms.ValidationError("Please fill in all card details for card payments.")
        
        return cleaned_data

class LoginForm(AuthenticationForm):
    username = forms.CharField(
        label="Username",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Username',
            'autocomplete': 'username',
            'autofocus': True
        })
    )
    password = forms.CharField(
        label="Password",
        strip=False,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Password',
            'autocomplete': 'current-password'
        })
    )
