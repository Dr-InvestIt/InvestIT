from django import forms
from .models import Stock

class StockForm(forms.ModelForm):
    class Meta:
        model = Stock
        fields = [
            'ticker1',
            'ticker2',
        ]
