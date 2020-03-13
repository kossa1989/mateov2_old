# Create your views here.
from django import forms
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .forms import AnalysisForm
from main import AnalyseData
from .models import Analyses
from .config_templates import templates
AnalysisForm = AnalysisForm

@login_required
def run_pytar(request):
    user_analyses = Analyses.objects.filter(user=request.user)
    if request.method == 'POST':
        form = AnalysisForm(request.POST)
        if form.is_valid():
            Analyses.objects.get_or_create(user=request.user,
                                    **form.cleaned_data)
            # clean up grouping to pass as python obj
            value = form.cleaned_data['case_group']
            form.cleaned_data['case_group'] = [i.strip() for i in value.split(',')]
            analysis = AnalyseData(**form.cleaned_data)
            analysis.main()
    elif 'id' in request.GET:
            tar = Analyses.objects.get(pk=int(request.GET['id']))
            #check if allowed user enters tar
            assert tar.user==request.user, 'Brak dostępu :P'
            form = AnalysisForm(data=tar.__dict__)
            for i in form.fields:
                # if loads save analysis set to readonly
                form.fields[i].widget.attrs['readonly']=True

    else:
        data = {}
        if 'load_template' in request.GET:
            data = templates[request.GET['load_template']]

        form = AnalysisForm(data=data)

    context = {'form': form,
               'user_analyses': user_analyses,
               'config_templates':templates,}

    return render(request, 'analysis/index.html', context)


def home_page(request):
    context = {}
    return render(request, 'index.html', context)