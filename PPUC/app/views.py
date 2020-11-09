"""
Definition of views.
"""

from datetime import datetime
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q
from django.http import HttpRequest
from .models import *
from app.forms import *
from django.views.generic import ListView, FormView
from django.contrib.auth import login as auth_login
from django.contrib.auth.decorators import login_required
import re
import nltk
from nltk.tokenize import sent_tokenize

def home(request):
    """Renders the home page."""
    context = {
        'title':'Home Page',
        'year':datetime.now().year,
        }
    assert isinstance(request, HttpRequest)
    return render(
        request,
        'app/index.html',
        context
    )

def contact(request):
    """Renders the contact page."""
    assert isinstance(request, HttpRequest)
    return render(
        request,
        'app/contact.html',
        {
            'title':'Contact',
            'message':'Contact page.',
            'year':datetime.now().year,
        }
    )

def about(request):
    """Renders the about page."""
    assert isinstance(request, HttpRequest)
    return render(
        request,
        'app/about.html',
        {
            'title':'About',
            'message':'application description page.',
            'year':datetime.now().year,
        }
    )

def search(request):
    context = {}
    query = request.GET.get('q','')
    locations = Location.objects.filter(Q(name__icontains=query))

    context = {
        'title' : 'Search',
        'locations' : locations,
        }
    assert isinstance(request, HttpRequest)
    return render(
        request,
        'app/search.html',
        context
    )

def search_contract(request):
    context = {}
    query = request.GET.get('q','')
    searched_term = request.GET.get('q')
    if query == '':
        results = ''
    else:
        results = []
        querySet = Sentence.objects.filter(Q(text__icontains=query))
        for result in querySet:
            t = result.text
            q_length = len(searched_term)
            pos = t.find(searched_term)
            #t = t[:pos] + "<span style=\"background-color: #FFFF00\">" + t[pos:pos+q_length] + "</span>" + t[pos+q_length:]
            #result.text=t
            result.first = t[:pos]
            result.second = t[pos:pos+q_length]
            result.third = t[pos+q_length:]
            results.append((result))
        context = {
            'title' : 'Search Contracts',
            'results' : results,
            }
    assert isinstance(request, HttpRequest)
    return render(
        request,
        'app/search_contract.html',
        context
    )

def view_location(request, lid):
    context = {}
    location = Location.objects.get(pk=lid)
    sentences = Sentence.objects.filter(Q(location=location))
    context = {
        'title' : 'View Location',
        'location' : location,
        'sentences' : sentences,
        'form' : ProblematicLanguageForm
        }
    assert isinstance(request, HttpRequest)
    return render(request,'app/view_location.html',context)

@login_required(login_url='login')
def edit_sentence(request, sid):
    sentence = Problematic_Sentence.objects.get(id=sid)
    if request.method == 'POST':
        form = ProblematicLanguageForm(request.POST)
        if form.is_valid():
            sentence.refresh_from_db()
            sentence.impact = form.cleaned_data.get('impact')
            sentence.limit_oversight = form.cleaned_data.get('limit_oversight')
            sentence.city_pay_for_misconduct = form.cleaned_data.get('city_pay_for_misconduct')
            sentence.erase_misconduct = form.cleaned_data.get('erase_misconduct')
            sentence.disqualify_complaints = form.cleaned_data.get('disqualify_complaints')
            sentence.restrict_interrogation = form.cleaned_data.get('restrict_interrogation')
            sentence.unfair_information = form.cleaned_data.get('unfair_information')
            sentence.save()
            location = Location.objects.filter(Q(name__icontains=sentence.location)).first()
            lid = location.id
            return view_location(request, lid)
    else:
        form = ProblematicLanguageForm(instance=sentence)
        return render(request, 'app/edit_sentence.html', {'title' : 'Edit Sentence','form': form, 'sentence' : sentence})

def complaint(request,lid):
    location = Location.objects.get(pk=lid)
    questions = location.questions.all()
    context = {}
    searchTerm = request.GET.get('searchTerm','')
    if searchTerm != '':
        results = Sentence.objects.filter(Q(location=location),Q(text__icontains=searchTerm))
    else:
        results = ''
    context = {'title': 'Complaints', 'location' : location, 'questions': questions, 'results' : results}
    return render(request,'app/complaint.html', context)
