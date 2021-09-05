from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseRedirect, Http404
from django.shortcuts import render
from django.urls import reverse
from django import forms
from django.forms import ModelForm, TextInput, Textarea
from django.contrib.auth.decorators import login_required

from .models import User, Listing, Bid, Comment

class NewListingForm(ModelForm):
	""" Used to create the Form for a New Listing """
	class Meta:
		model = Listing
		fields = ['title', 'description', 'starting_bid', 'photo', 'category']
		widgets = {
			'title': forms.TextInput(attrs={
				'class': 'form-control',
				'placeholder': 'Enter a Title...'
				}),
			'description': forms.Textarea(attrs={
				'class': 'form-control',
				'placeholder': 'Enter a Description...'
				}),
			'starting_bid': forms.NumberInput(attrs={
				'class': 'form-control',
				'placeholder': '15.00',
				'min': '0.01',
				'max': '2500'
				}),
			'photo': forms.URLInput(attrs={
				'class': 'form-control',
				'placeholder': 'https://example.com',
				'pattern':'https://.*'
				}),
			'category': forms.TextInput(attrs={
				'class': 'form-control',
				'placeholder': 'Fashion, Toys, Electronics, etc...'
				})
		}
		
class NewBidForm(ModelForm):
	""" Used to create the Form for a Bid """
	def __init__(self, *args, **kwargs):
		""" 
		Init method is used to set the min_bid.
		Min bid is dynamically set based on current bid.
		"""
		min_bid = kwargs.pop('arg', 0.05)
		super(NewBidForm, self).__init__(*args, **kwargs)
		print("min_bid=",min_bid)
		self.fields['bid'].widget.attrs.update(
            {'min': min_bid},
        )
	class Meta:
		model = Bid
		fields = ['bid']
		widgets = {
			'bid': forms.NumberInput(attrs={
				'class': 'form-control',
				#'placeholder': '15.00',
				'max': '2500'
				})
		}
		
class NewCommentForm(ModelForm):
	""" Used to create the Form for a Bid """
	class Meta:
		model = Comment
		fields = ['comment']
		widgets = {
			'comment': forms.Textarea(attrs={
				'class': 'form-control',
				'placeholder': 'Enter a Comment...'
				})
		}
		
def index(request):
    return render(request, "auctions/index.html", {
		# Exclude listings that are NOT active
		"listings": Listing.objects.exclude(active=False)
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

@login_required(login_url='login')
def createlisting(request):
	"""
	Function to allow a user to create a new auction listing.
	"""
	# Check if user submitted a new listing post
	if request.method == "POST":

		form = NewListingForm(request.POST)
		# Validate the form
		if form.is_valid():
			listing = form.save(commit=False) # allow us to change fields manually
			# Add information that wasn't on user form
			listing.current_price = form.cleaned_data["starting_bid"]
			#listing.current_price = 0.0
			listing.user = request.user
		
		# Save the listing to the Database
		listing.save()
		# Return User to New Listing
		return HttpResponseRedirect(reverse("listing", args=(listing.id,)))
	else:
		return render(request, "auctions/createlisting.html", {"form": NewListingForm()})
		
def listing(request, listing_id):
	"""
	Display a listing to a user
	"""
	listing = Listing.objects.get(pk=listing_id) # get listing object using id
	
	bids = listing.listing_bid.all() # retrieve the bid objects for this listing
	bid_count = len(bids) # count number of bid objects
	
	# Need to determine minimum bid amount
	current_price = listing.current_price
	starting_bid = listing.starting_bid

	if current_price > starting_bid:
		min_bid = float(current_price) + 0.01
	else:
		min_bid = starting_bid
		
	# Get the highest bidder when auction is closed
	if bid_count > 0:
		highest_bidder = bids[bid_count-1].user
	else:
		highest_bidder = None
		
	# Determine if user is watching this listing
	# This will be passed to the template to determine whether to show
	# a Watch or Unwatch button
	if request.user in listing.watchlist.all():
		watch = True
	else:
		watch = False
	
	return render(request, "auctions/listing.html", {
		"listing":listing,
		"bid_count": bid_count,
		"min_bid": min_bid,
		"form": NewBidForm(arg=min_bid),
		"highest_bidder": highest_bidder,
		"watch": watch,
		# Use the related name (from Models) to get the comments for the listing
		"comments": listing.listing_comment.all(),
		"comment_form": NewCommentForm()
	})

@login_required(login_url='login')
def comment(request, listing_id):
	"""
	Function to allow a user to post a comment.
	"""
	
	# Check if user submitted a new comment post
	if request.method == "POST":

		form = NewCommentForm(request.POST)
		# Validate the form
		if form.is_valid():
			comment = form.save(commit=False) # allow us to fields manually
			# Add information that wasn't on user form
			#comment.comment = form.cleaned_data["comment"]
			# Listing
			comment.listing = Listing.objects.get(pk=listing_id)
		
		# Save the listing to the Database
		comment.save()
		# Return User Back to Listing
		return HttpResponseRedirect(reverse("listing", args=(listing_id,)))
	
	else:
		return HttpResponseRedirect(reverse("listing", args=(listing_id,)))
		
@login_required(login_url='login')
def bid(request, listing_id):
	"""
	Place a bid on an active listing
	"""
	# Check if user submitted a new bid
	if request.method == "POST":		
		
		# Take in the data the user submitted
		form = NewBidForm(request.POST)
		
		# Check if form data is valid (server-side)
		if form.is_valid():
			# Update the bid table
			bid = form.save(commit=False) # allow us to fields manually
			bid.user = request.user
			bid.listing = Listing.objects.get(pk=listing_id)
			
			# Update the current_price for the listing table
			bid.listing.current_price = form.cleaned_data["bid"]
		
		# Save the listing to the Database
		bid.save()
		bid.listing.save(update_fields=["current_price"]) 
		
		# Return User to Webpage
		# Can't put .html after listing
		# Can't put auctions\ before listing
		return HttpResponseRedirect(reverse("listing", args=(listing_id,)))
	
	else:
		return HttpResponseRedirect(reverse("listing", args=(listing_id,)))

@login_required(login_url='login')
def closeauction(request, listing_id):
	"""
	Close an auction for an item listing
	"""
	if request.method == "POST":		
		
		# Update the active field to be False (closed)
		listing = Listing.objects.get(pk=listing_id)
		listing.active = False
		# Since other fields aren't changing, just specify
		# the field that changed when saving, otherwise
		# an error will occur.
		listing.save(update_fields=['active'])
		
		# Return User to Webpage
		# Can't put .html after listing
		# Can't put auctions\ before listing
		return HttpResponseRedirect(reverse("listing", args=(listing_id,)))
	
	else:
		return HttpResponseRedirect(reverse("listing", args=(listing_id,)))

@login_required(login_url='login')
def watchlist(request):
	"""
	Get the user's watchlist from listings
	"""
	# Get all listings
	listings = Listing.objects.all()
	# Create a list to store listings watched by user
	watchlist = []
	# Iterate over the listings.  Wasn't sure how
	# do this using a list comprehension.
	for listing in listings:
		# Create a list of the watchers for a listing
		watchers = [watcher for watcher in listing.watchlist.all()]
		# Check if the user if one of the watchers
		if request.user in watchers:
			# If user is a watcher, then append the listing
			watchlist.append(listing)

	return render(request, "auctions/watchlist.html", {
		# Exclude listings that are NOT on Watchlist
		"listings": watchlist
	})

@login_required(login_url='login')
def watch(request, listing_id):
	"""
	Add and Remove a user from a listing watchlist
	"""
	if request.method == "POST":		

		# Get listing
		listing = Listing.objects.get(pk=listing_id)
		
		# Check if user was already watching
		if request.user in listing.watchlist.all():
			# Remove user from watchlist
			listing.watchlist.remove(request.user)
		else:
			# Add user to watchlist
			listing.watchlist.add(request.user)
		
		# Save the listing
		listing.save()
		
		# Return User to Webpage
		# Can't put .html after listing
		# Can't put auctions\ before listing
		return HttpResponseRedirect(reverse("listing", args=(listing_id,)))
	
	else:
		return HttpResponseRedirect(reverse("listing", args=(listing_id,)))
		
def categories(request):
	""" 
	Display list of clickable categories 
	
	Presents all categories even for auctions that have ended.
	User can select a category and then the user will be redirected to
	the category page for the selected category.
	"""
	listings = Listing.objects.all()
	
	# Create a set to avoid duplicates
	categories= set()
	
	for listing in listings:
		# Don't store empty categories
		if listing.category is not "":
			categories.add(listing.category)
	return render(request, "auctions/categories.html", {"categories": categories})
	
def category(request, category_name):
	"""
	Display listings in certain category
	
	User will select a category from the categories page and this function will run
	to determine which ACTIVE listings are in the selected category.
	"""
	# Filter to find listings that match the category and are also active
	listings = Listing.objects.filter(category = category_name, active = True)
	
	return render(request, "auctions/category.html", {"listings": listings})
	