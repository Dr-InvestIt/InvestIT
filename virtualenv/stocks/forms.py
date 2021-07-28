from django import forms
from .models import Stock


class StockForm(forms.ModelForm):
    class Meta:
        model = Stock
        fields = [
            'stock_id'
        ]


class GraphForm(forms.Form):
    graph = forms.CharField(label='Which graph do you want?', widget=forms.Select(
        choices=[("volatility", "Volatility"), ("efficient-frontier", "Efficient Frontier")]))
