from django import forms
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from .models import User, AuctionListings, Bids, Category, Watchlist, Comments
from django.contrib import messages

def index(request):
    
    auctionlist = AuctionListings.objects.all().order_by('price')
    if request.user.is_authenticated:
        return render(request, "auctions/index.html",{
            "auctionlist": auctionlist,
            "count": Watchlist.objects.filter(user=request.user).all().count()
        })
    else:
        return render(request, "auctions/index.html",{
            "auctionlist": auctionlist,
            
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
    

class NewForm(forms.ModelForm):
    class Meta:
        model = AuctionListings
        fields=['title','description','image', 'category', 'price']
        widgets = {
            'title':forms.TextInput(attrs={'class':'form-control'}),
            'description':forms.Textarea(attrs={'class':'form-control'}),
            'image':forms.TextInput(attrs={'class':'form-control'}),
            
        }

class FormComments(forms.ModelForm):
    class Meta:
        model = Comments
        fields = ['comments']
        widgets = {            
            'comments':forms.Textarea(attrs={'class':'form-control'}),           
        }

class FormBid(forms.ModelForm):
    class Meta:
        model = Bids
        fields = ['bids']


def categories(request):
    return render(request, "auctions/categories.html", {
                "list": Category.objects.all(),
                "count": Watchlist.objects.filter(user=request.user).all().count()
            })


def post_category(request, id):
    category = Category.objects.get(pk=id)
    auctionlist = AuctionListings.objects.filter(category=category)
    return render(request, "auctions/index.html",{
        "auctionlist": auctionlist,
        "count": Watchlist.objects.filter(user=request.user).all().count()
        
    })


def listings(request, id):
    
    data = AuctionListings.objects.get(pk=id)
    all_comments = Comments.objects.filter(item=data).all()
    comments_form = FormComments()
    
    
    
    bid_count = Bids.objects.filter(item=data).all().count()
    bid_form = FormBid()
    bid_form.item = data
    user = request.user
    if request.user.is_authenticated:
        watched = Watchlist.objects.filter(user=request.user.id, item=data)
        watch_count = Watchlist.objects.filter(user=request.user).all().count()
        if bid_count > 0:
            
            return render(request, "auctions/listings.html", {
                "watched": watched,
                "user":user,
                "count": watch_count,
                "form": data,
                "bids": Bids.objects.latest('date'),
                "bid": bid_form,
                "bid_count": bid_count,
                "comment_form": comments_form,
                "all_comments": all_comments
                })
        else:
            return render(request, "auctions/listings.html", {
                "watched": watched,
                "user":user,
                "count": watch_count,
                "form": data,
                "bids":  Bids.objects.all(),
                "bid": bid_form,
                "bid_count": bid_count,
                "comment_form": comments_form,
                "all_comments": all_comments
                })
    else:
        return render(request, "auctions/listings.html", {
            "bid_count": bid_count,
            "form": data,
            "bid": bid_form,
            "comment_form": comments_form,
            "all_comments": all_comments
            })


@login_required
def watchlist(request, id):
    
    items = get_object_or_404(AuctionListings, pk=id)
    watched = Watchlist.objects.filter(user=request.user, item=items)
    
    if request.method == 'POST':
        if watched.exists():
            watched.delete()
            return redirect(reverse('listings', args=[id]))       
        else:
            watched, created = Watchlist.objects.get_or_create(user=request.user, item=items)
            watched.save()
            return HttpResponseRedirect(reverse("watch"))
        

@login_required    
def watch(request):
    watch_count = Watchlist.objects.filter(user=request.user).all().count()
    watched = watched = Watchlist.objects.filter(user=request.user)
    return render(request, "auctions/watchlist.html",{
            "watchlist": watched,
            "count": watch_count,   
            })


@login_required
def create(request):
    
    if request.method == 'POST':
        form = NewForm(request.POST)
        if form.is_valid():
            auction = form.save(commit=False)
            
            auction.user = request.user
            auction.save()
            return redirect(reverse('listings', args=[auction.id])) 
        else:
                
            form = NewForm()
            return render(request, "auctions/create.html", {
                "form": form,
                "count": Watchlist.objects.filter(user=request.user).all().count()
            })
    
    else:
        form = NewForm()
        return render(request, "auctions/create.html", {
            "form": form,
            "count": Watchlist.objects.filter(user=request.user).all().count()
        })
    
@login_required
def post_bid(request, id):
       
    if request.method == "POST":
        bid_form = FormBid(request.POST)
        auction = AuctionListings.objects.get(pk=id)
        
        if bid_form.is_valid():
            bid = bid_form.save(commit=False)
            bid.item = auction
            
            if (int(bid.bids) > auction.price) and (int(bid.bids) > bid.item.current_bid):
                
                bid.user = request.user
                
                bid.item.current_bid = int(bid.bids)
                auction.current_bid = int(bid.bids)
                auction.save()
                bid.save()
                
            else:
                messages.error(request, 'The Bid should be greater than current bid')
                
           
                     
            return redirect(reverse('listings', args=[auction.id]))
                
@login_required
def post_comment(request, id):
      
    auction = AuctionListings.objects.get(pk=id)
    if request.method == "POST":
        comment_form = FormComments(request.POST)
        
        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.item = auction
            comment.user = request.user
            comment.save()
                
                    
            return redirect(reverse('listings', args=[auction.id]))
        
@login_required        
def closed(request, id):
    data = AuctionListings.objects.get(pk=id)
    watched = Watchlist.objects.filter(item=data)
    if request.method == "POST":
        if watched.exists():
            watched.delete()
        data = AuctionListings.objects.get(pk=id)
       
        
        data.closed = True          
        data.save()
        
        return redirect(reverse('listings', args=[data.id]))
    