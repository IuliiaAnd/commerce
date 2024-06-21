from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass

class Category(models.Model):
    category_name = models.CharField(max_length=64)

    def __str__(self):
        return self.category_name
    
class Listing(models.Model):
    title = models.CharField(max_length=64)
    description = models.TextField()
    starting_price = models.DecimalField(max_digits=6, decimal_places=2)
    date = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, default=None)
    image = models.ImageField(upload_to="media", default="media/fallback.png", blank=True)
    watchlist = models.ManyToManyField(User, blank=True, null=True, related_name="watchlist")
    category = models.ForeignKey(Category, on_delete=models.CASCADE, blank=True, null=True)
    active = models.BooleanField(default=True) 
       
    
    def __str__(self):
        return self.title
    
class Comments(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, default=None)    
    content = models.CharField(max_length=64)
    date = models.DateTimeField(auto_now_add=True)
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return f"{self.author} comment on {self.listing}"

class Bid(models.Model):    
    author = models.ForeignKey(User, on_delete=models.CASCADE, default=None)
    new_bid =  models.DecimalField(max_digits=6, decimal_places=2)
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, null=True, related_name="bids")    

    def __str__(self):
        return f"{self.author} placed a bid ${self.new_bid} on {self.listing}"