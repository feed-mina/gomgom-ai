# gomgom_ai/views.py
from django.shortcuts import render

def main(request):
    return render(request, 'gomgom_ai/main.html')

