from django.forms import ModelForm
from django import forms
from .models import Analyses


class AnalysisForm(ModelForm):
    class Meta:
        model = Analyses
        exclude = ['user','config',]

    n_cols = 60
    path = forms.CharField(widget=forms.Textarea(attrs={'rows': 4, 'cols': n_cols, 'placeholder': 'Ścieżka w której zostanie zapisana analiza. '
                                                                                                  'Jest to katalog roboczy dla danej taryfy'}), label='Ścieżka',
                           help_text="Wpisz ścieżkę na dysku T:\ gdzie będzie przeprowadzana analiza.")
    query_sm = forms.CharField(widget=forms.Textarea(attrs={'rows': 8, 'cols': n_cols, 'placeholder': 'Wpisz tutaj polecenie, które posłuży do wyliczenia Taryfy. Możesz wybrać z szablonu na górze np. na_pacjenta'}))
    name = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Nazwa własna, dla obecnego szablonu. Nazwa nie może się powatarzać'}), label='Nazwa taryfikatora')
    schema = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Schemat bazy danych, by wybrac dane z 2017 wpisz "wb17"'}),label='Schemat', initial='wb17')
    case_group = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Grupowanie analizy, np. kod_prod,kod_sw,nr_ks'}),label='Grupowanie')
    permissive = forms.BooleanField(label='Czy dopuszczasz błędy?', required=False)
