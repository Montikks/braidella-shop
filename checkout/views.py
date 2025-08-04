from django.shortcuts import render

def address(request):
    return render(request, "checkout/address.html")

def review(request):
    return render(request, "checkout/review.html")
