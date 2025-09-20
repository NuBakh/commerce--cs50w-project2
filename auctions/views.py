from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect 
from django.urls import reverse
from django.forms import ModelForm
from django import forms
from .models import User ,Listing, Comment, Bid
from django.db.models import Max
from django.contrib import messages
from django.shortcuts import render, redirect


class ListingForm(ModelForm):
    class Meta:
        model = Listing
        fields = ["title", "description", "starting_bid", "image_url", "category"]
        
class BidForm(ModelForm):
    class Meta:
        model=Bid
        fields=['amount']
        
class CommentForm(ModelForm):
    class Meta:
        model=Comment
        fields=["comment"]
    

def create(request):
    if request.method == "POST":
        form=ListingForm(request.POST)
        if form.is_valid():
           listing=form.save(commit=False)
           listing.owner=request.user
           listing.save()

        return HttpResponseRedirect(reverse("index"))
    else:
            form = ListingForm()         
    listings=Listing.objects.all()    
    return render(request, "auctions/create.html",{
            "form":form,
            "listings":listings
                })
    
   
def watchlist (request):
    list=request.user.watchlist.all()

    
    if request.method=="POST":
        listid=request.POST.get("listing_id")
        listing=Listing.objects.get(id=listid)
        if listing in request.user.watchlist.all():
            request.user.watchlist.remove(listing)
        else:
            request.user.watchlist.add(listing)
            
        return redirect("watchlist")

    return render(request, "auctions/watchlist.html", {
        "list":list
    })
       
category=[]  
def categories(request):
    active_listings = Listing.objects.filter(active=True)
    listing=active_listings.values_list("category", flat=True)
    for list in listing:
        if list in category:
            continue
        else:
            category.append(list)
    
    return render(request, "auctions/categories.html",{
        'listing':category
    })
   
    
def detail(request, list_id):
    listing=Listing.objects.get(id=list_id)
    startingbid=listing.starting_bid
    bids=listing.listbid.all() 
    comment=listing.comment_listing.all()
    max_price = bids.aggregate(Max("amount"))['amount__max']
    higest_bid=bids.filter(amount=max_price).first()

    form=BidForm()
    formComment=CommentForm()
    
    if request.method=="POST":
        if "close" in request.POST and listing.owner==request.user:
         
            listing.active=False
            if higest_bid:
                listing.winner=higest_bid.user
            

            listing.save()
            return redirect('detail',list_id=listing.id)            
        
        if "submit_bid" in request.POST:
            
            form=BidForm(request.POST)
        
            if form.is_valid():
                new_bid=form.cleaned_data["amount"]
                if max_price==None:
                    max_price=startingbid
            
                if new_bid>max_price:
                        bid= form.save(commit=False)   
                        bid.user=request.user
                        bid.listing=listing
                        bid.save()
                        return redirect('detail',list_id=listing.id)
               

        elif "submit_comment" in request.POST:
            formComment=CommentForm(request.POST)
            if formComment.is_valid():

                usecomment=formComment.save(commit=False)
                usecomment.user=request.user
                usecomment.listing=listing
                usecomment.save()
                return redirect('detail',list_id=listing.id)        
       
    return render (request, "auctions/detail.html", {
        "listing":listing,
        "bids":bids,
        "form":form,
        "prize":max_price,
        "formComment":formComment,
        "comment":comment   
    })
  
def activelist(request, category_name):
    listings = Listing.objects.filter(category=category_name, active=True)

    
    return render(request, "auctions/activelist.html", {
        "listings":listings
    })
   


def index(request):
    listings = Listing.objects.filter(active=True)
    return render(request, "auctions/index.html", {"listings": listings})


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")
    
    
    

