from django import forms
from .models import User, Product

class SignupForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    password_confirm = forms.CharField(widget=forms.PasswordInput, label="Confirm Password")

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'phone', 'address']

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        password_confirm = cleaned_data.get("password_confirm")

        if password != password_confirm:
            raise forms.ValidationError("Passwords do not match")
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
