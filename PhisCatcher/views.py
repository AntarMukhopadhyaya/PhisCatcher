from django.shortcuts import render, redirect


def home(request):
  return render(request,"home.html")


def about(request):
  return render(request,'contributors.html')
def contributors(request):
  return render(request,'contributors.html')