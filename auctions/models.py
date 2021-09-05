from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
	pass
	
	
class Listing(models.Model):
	"""
	Model for Auction Listings.
	Listing includes: title, description, starting bid, current price, photo, category.
	"""
	title = models.CharField(max_length=64)
	description = models.CharField(max_length=600)
	starting_bid = models.DecimalField(max_digits=6, decimal_places=2)
	current_price = models.DecimalField(max_digits=6, decimal_places=2)
	photo = models.URLField(max_length=200, blank=True)
	category = models.CharField(max_length=12, blank=True)
	user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_listing")
	active = models.BooleanField(default=True)
	watchlist = models.ManyToManyField(User, blank=True, related_name="watchers", default=None)
	
	
class Bid(models.Model):
	"""
	Model for bids placed on auction listings.
	We need information on each user that made a bid, which item they bid on,
	and how much the bid was for.
	"""
	listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="listing_bid")
	bid = models.DecimalField(max_digits=6, decimal_places=2)
	user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_bid")
	
class Comment(models.Model):
	"""
	Model for comments made on auction listing
	We don't need to keep track of who made the comment, but we need to know
	the listing being commented on and what the comment was.
	"""
	listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="listing_comment")
	comment = models.CharField(max_length=128)
	#user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_comment")
	


