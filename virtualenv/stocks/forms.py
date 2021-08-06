from django import forms
from django.forms.widgets import Widget
from .models import Stock


class StockForm(forms.ModelForm):
    class Meta:
        model = Stock
        fields = ['stock_id']
        widgets = {
            'stock_id':
            forms.TextInput(
                attrs={
                    'class': 'form-control form-control-lg',
                    'placeholder': 'eg.AAPL,TSM,FB'
                })
        }


class EfficientForm(forms.ModelForm):
    class Meta:
        model = Stock
        fields = ['stock_id', 'stock_value']
        widgets = {
            'stock_id':
            forms.TextInput(
                attrs={
                    'class': 'form-control form-control-lg',
                    'placeholder': 'eg.AAPL,TSM,FB'
                }),
            'stock_value':
            forms.TextInput(
                attrs={
                    'class': 'form-control form-control-lg',
                    'placeholder': 'eg.0-99999'
                }),
            # 'Enter your own portfolio': forms.CheckboxInput(attrs={'class':'form-control form-control-lg'})
        }


class GraphForm(forms.Form):
    graph = forms.CharField(
        label='Which graph do you want?',
        widget=forms.Select(choices=[(
            "volatility",
            "Volatility"), ("efficient-frontier", "Efficient Frontier")]))
