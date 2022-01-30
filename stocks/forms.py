from django import forms
from django.forms.widgets import Widget
from .models import Stock

#Django provides a range of tools and libraries to help you build forms to accept input from site visitors, 
# and then process and respond to the input.

class StockForm(forms.ModelForm):
    class Meta:
        model = Stock
        fields = ['stock_id']
        widgets = {
            'stock_id':
            forms.TextInput(
                attrs={
                    'class': 'form-control form-control-lg',
                    'placeholder': 'eg.AAPL,TSM,FB',
                    'list': 'stocklist'
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
                    'placeholder': 'eg.AAPL,TSM,FB',
                    'list': "stocklist",
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
