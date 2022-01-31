from django import forms


class SearchForm(forms.Form):
    search = forms.CharField(min_length=3, required=False)
    search_in = forms.ChoiceField(choices=[('title', 'Title'), ('contributor', 'Contributor')], required=False)
