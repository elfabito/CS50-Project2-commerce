from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models



class User(AbstractUser):
    pass


class Category(models.Model):
    name = models.CharField(max_length=50)
    
    def __str__(self):
        return self.name
    
    
class AuctionListings(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=50)
    description = models.TextField()
    image = models.CharField(max_length=150, default="https://www.idsplus.net/wp-content/uploads/default-placeholder-300x300.png")
    price = models.IntegerField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)
    closed = models.BooleanField(default=False)
    current_bid = models.IntegerField(default=0)

    def __str__(self):
        return self.title
    
    
class Bids(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    bids = models.CharField(max_length=50)   
    item = models.ForeignKey(AuctionListings, on_delete=models.CASCADE)
    
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user}: bid - {self.bids}"
    
    
class Watchlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    item = models.ForeignKey(AuctionListings, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user}'s watchlist"


class Comments(models.Model):
    item = models.ForeignKey(AuctionListings, on_delete=models.CASCADE, related_name="comments")
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    comments = models.TextField()
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user}: {self.comments}"