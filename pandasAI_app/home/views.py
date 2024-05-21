from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.
def home_page(request, *kwarg, **kwargs):
    template_arg={}
    return render(request, 'home/home.html', template_arg)
