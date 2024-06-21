from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse

from .models import User, Listing, Comments, Category, Bid
from django import forms
from django.contrib.auth.decorators import login_required
from django.contrib import messages


def index(request):
    listings = Listing.objects.all().order_by('-date')    
    return render(request, "auctions/index.html", {
        "listings": listings
    })

def listing_page(request, id):
    listings = Listing.objects.get(pk=id)
    in_watchlist = request.user in listings.watchlist.all()
    comment_form = AddComment()
    all_comments = Comments.objects.filter(listing=listings).order_by('-date')
    bid_form = AddBid()
    all_bids = Bid.objects.filter(listing=listings).order_by('-new_bid')
    is_user = request.user == listings.author
    is_active = listings.active

    winner_message = None
    winner = None
    if not is_active:
        highest_bid = Bid.objects.filter(listing=listings).order_by('-new_bid').first()
        if highest_bid:
            winner = highest_bid.author
            winner_message = f'{highest_bid.author.username} won the bid with ${highest_bid.new_bid}.'
        else:            
            winner_message = 'No bids were placed on this listing.'
      
    return render(request, "auctions/listing_page.html", {
        "listing": listings,
        "in_watchlist":in_watchlist,
        "comment_form": comment_form,
        "all_comments": all_comments,
        "bid_form": bid_form,
        "is_user": is_user,
        "is_active": is_active,
        "winner_message": winner_message,
        "all_bids": all_bids,
        "winner":winner 
    }) 

class CreateListing(forms.ModelForm):
    class Meta:
        model = Listing
        fields = ['title', 'description', 'starting_price', 'image', 'category']

def new_listing(request):
    if request.method == "POST":
        form = CreateListing(request.POST, request.FILES)
        if form.is_valid():
            new_post = form.save(commit=False)
            new_post.author = request.user
            new_post.save()
            return redirect("index")    
    else:    
        form = CreateListing()
        return render(request, "auctions/create_listing.html", {
            "form": form
        })
    
def watchlist_page(request):
    current_user = request.user
    listings = current_user.watchlist.all()
    return render(request, "auctions/watchlist.html",{
        "listings": listings
    })

def add_to_watchlist(request, id):
    listing = Listing.objects.get(pk=id)
    current_user = request.user
    listing.watchlist.add(current_user)
    return HttpResponseRedirect(reverse("listing_page", args=(id, ))) 

def remove_from_watchlist(request, id):
    listing = Listing.objects.get(pk=id)
    current_user = request.user
    listing.watchlist.remove(current_user)
    return HttpResponseRedirect(reverse("listing_page", args=(id, )))

class AddComment(forms.ModelForm):
    class Meta:
        model = Comments
        fields = ['content']
        widgets = {
            'content': forms.TextInput(attrs={'placeholder': 'Add Comment'}),
        }

@login_required(login_url='login')
def add_comment(request, id):
    listing = Listing.objects.get(pk=id)

    if request.method == "POST":
        comment_form = AddComment(request.POST)
        if comment_form.is_valid():
            new_message = comment_form.save(commit=False)
            new_message.author = request.user
            new_message.listing = listing 
            new_message.save()            
            return HttpResponseRedirect(reverse("listing_page", args=(id, )))
    else:                
        comment_form = AddComment()        
    
    return render(request, "auctions/listing_page.html", {
        "comment_form": comment_form,
        "listing": listing,
    })
    
def filter_by_category(request, category_id):    
    category = Category.objects.get(pk=category_id)
    listings = Listing.objects.filter(category=category, active=True)
    return render(request, "auctions/filter_category.html", {
        "category": category,
        "listings": listings
    })

def category_list(request):
    all_categories = Category.objects.all()
    return render(request, "auctions/categories.html", {
            "all_categories": all_categories
        })

class AddBid(forms.ModelForm):
    class Meta:
        model = Bid
        fields = ['new_bid']

def new_bid(request,id):
    listing = Listing.objects.get(pk=id)
    if not listing.active:
        messages.error(request, 'This listing is no longer active')
        return HttpResponseRedirect(reverse("listing_page", args=(id, )))

    starting_bid = listing.starting_price
    highest_bid = Bid.objects.filter(listing=listing).order_by('-new_bid').first()
    current_highest_bid = highest_bid.new_bid if highest_bid else None

    if request.method == "POST":
        bid_form = AddBid(request.POST)
        
        if bid_form.is_valid():
            new_bid_value = bid_form.cleaned_data['new_bid']
            
            if current_highest_bid is not None:
                # If there are existing bids, new bid must be higher than the current highest bid
                if new_bid_value > current_highest_bid:
                    place_bid = bid_form.save(commit=False)
                    place_bid.author = request.user
                    place_bid.listing = listing
                    place_bid.save()

                    # Update new bid value on the listing
                    listing.starting_price = new_bid_value
                    listing.save()

                    messages.success(request, 'Your bid has been successfully placed!')
                    return HttpResponseRedirect(reverse("listing_page", args=(id, )))
                else:
                    messages.error(request, 'New bid should be higher than the current highest bid.')
                    return HttpResponseRedirect(reverse("listing_page", args=(id, )))
            else:
                # If no existing bids, new bid can be equal to or higher than the starting bid
                if new_bid_value >= starting_bid:
                    place_bid = bid_form.save(commit=False)
                    place_bid.author = request.user
                    place_bid.listing = listing
                    place_bid.save()
                    
                    listing.starting_price = new_bid_value
                    listing.save()

                    messages.success(request, 'Your bid has been successfully placed!')
                    return HttpResponseRedirect(reverse("listing_page", args=(id, )))
                else:
                    messages.error(request, 'New bid should be equal to or higher than the starting price.')
                    return HttpResponseRedirect(reverse("listing_page", args=(id, )))
        else:
            messages.error(request, 'Invalid bid form submission.')

    else:
        bid_form = AddBid()

    return render(request, "auctions/listing_page.html", {
        "bid_form": bid_form,
        "listing": listing,
    })
    
def close_listing(request, id):
    listing = Listing.objects.get(pk=id)
    current_user = request.user       
    if current_user == listing.author:
        listing.active = False
        listing.save()
        messages.success(request,'Auction Closed!')
        
        highest_bid = Bid.objects.filter(listing=listing).order_by('-new_bid').first()

        if highest_bid:            
            messages.success(request,f'{highest_bid.author.username} won the bid with ${highest_bid.new_bid}.')                
        else:
            messages.warning(request,'No bids were placed on this listing.')
    else:
        messages.error(request, 'You are not authorized to close this auction.')

    return HttpResponseRedirect(reverse("listing_page", args=(id, )))

def closed_auctions(request):
    closed_listings = Listing.objects.filter(active=False)    
    return render(request, "auctions/closed_auctions.html", {
        "listings": closed_listings
    })

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
