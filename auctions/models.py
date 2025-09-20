from django.contrib.auth.models import AbstractUser
from django.db import models
from django.forms import ModelForm





class Listing(models.Model):
     title=models.CharField(max_length=64)
     description=models.TextField(max_length=500)
     starting_bid=models.DecimalField(max_digits=10, decimal_places=2)
     image_url = models.URLField(max_length=200, blank=True, null=True)
     category=models.CharField(max_length=64)
     owner=models.ForeignKey("User", on_delete=models.CASCADE, related_name="listings")
     active=models.BooleanField(default=True)
     winner=models.ForeignKey("User", on_delete=models.CASCADE, null=True, blank=True, related_name="winner")


     def __str__(self):
            return f"{self.title} "
        
        
        
        
        
class User(AbstractUser):
    watchlist=models.ManyToManyField(Listing, blank=True, related_name="watch")
    pass
        
        
        
        
        
        
        
class Bid (models.Model):
    amount=models.DecimalField(max_digits=10, decimal_places=2)
    timestamp=models.DateTimeField(auto_now_add=True)
    user=models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_bid')
    listing=models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="listbid")
    
    
    def __str__(self):
         return f"{self.user} : {self.amount}$ "
     
     
     
     
     
     
class Comment (models.Model):
        user=models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_comment')
        comment=models.CharField(max_length=500)
        timestamp=models.DateTimeField(auto_now_add=True)
        listing=models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="comment_listing")

        def __str__(self):
              format="%Y.%m.%d"
              return f" {self.timestamp.strftime(format)}. {self.user} :'{self.comment}' "
          
          


