from django import forms

class NameForm(forms.Form):
    stockname = forms.CharField(label="Stock Name", help_text="Enter stock code", max_length=100)