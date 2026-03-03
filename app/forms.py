from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, Address, Feedback, Product, Category


class SignupForm(UserCreationForm):
    email      = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=100)
    last_name  = forms.CharField(max_length=100)

    class Meta:
        model  = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password1', 'password2']


class LoginForm(forms.Form):
    username = forms.CharField(max_length=150)
    password = forms.CharField(widget=forms.PasswordInput)
    is_admin = forms.BooleanField(required=False)


class AddressForm(forms.ModelForm):
    class Meta:
        model  = Address
        fields = ['first_name', 'last_name', 'address1', 'address2', 'city', 'zip_code', 'country']
        widgets = {
            'first_name': forms.TextInput(attrs={'class':'form-control','placeholder':'First Name'}),
            'last_name':  forms.TextInput(attrs={'class':'form-control','placeholder':'Last Name'}),
            'address1':   forms.TextInput(attrs={'class':'form-control','placeholder':'123 Fashion Ave'}),
            'address2':   forms.TextInput(attrs={'class':'form-control','placeholder':'Apt, Suite (optional)'}),
            'city':       forms.TextInput(attrs={'class':'form-control','placeholder':'City'}),
            'zip_code':   forms.TextInput(attrs={'class':'form-control','placeholder':'ZIP Code'}),
            'country':    forms.TextInput(attrs={'class':'form-control','placeholder':'Country'}),
        }


class FeedbackForm(forms.ModelForm):
    class Meta:
        model  = Feedback
        fields = ['headline', 'message', 'rating']
        widgets = {
            'headline': forms.TextInput(attrs={'class':'form-control','placeholder':"What's most important to know?"}),
            'message':  forms.Textarea(attrs={'class':'form-control','rows':5,'placeholder':'What did you like or dislike?'}),
            'rating':   forms.HiddenInput(),
        }


class ProductForm(forms.ModelForm):
    class Meta:
        model  = Product
        fields = ['name','description','price','old_price','category','image','image2','image3','sizes','stock','is_active','is_featured','badge']
        widgets = {
            'name':        forms.TextInput(attrs={'class':'form-control'}),
            'description': forms.Textarea(attrs={'class':'form-control','rows':3}),
            'price':       forms.NumberInput(attrs={'class':'form-control'}),
            'old_price':   forms.NumberInput(attrs={'class':'form-control'}),
            'category':    forms.Select(attrs={'class':'form-select'}),
            'sizes':       forms.TextInput(attrs={'class':'form-control','placeholder':'XS,S,M,L,XL'}),
            'stock':       forms.NumberInput(attrs={'class':'form-control'}),
            'badge':       forms.TextInput(attrs={'class':'form-control','placeholder':'NEW, SALE, etc.'}),
        }


class CategoryForm(forms.ModelForm):
    class Meta:
        model  = Category
        fields = ['name', 'description', 'image']
        widgets = {
            'name':        forms.TextInput(attrs={'class':'form-control'}),
            'description': forms.Textarea(attrs={'class':'form-control','rows':2}),
        }
