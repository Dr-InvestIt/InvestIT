from django import forms
from django.forms.widgets import Widget
from .models import Stock


class StockForm(forms.ModelForm):
    class Meta:
        model = Stock
        fields = [
            'stock_id'
        ]
        widgets = {
            'stock_id': forms.TextInput(attrs={'class':'form-control form-control-lg','placeholder': 'eg.AAPL,TSM,FB'})
        }

class GraphForm(forms.Form):
    graph = forms.CharField(label='Which graph do you want?', widget=forms.Select(
        choices=[("volatility", "Volatility"), ("efficient-frontier", "Efficient Frontier")]))
