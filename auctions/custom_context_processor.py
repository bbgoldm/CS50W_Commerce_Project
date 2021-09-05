from .models import User, Listing, Bid, Comment

def layout(request):
	"""
	Custom Context Processor used to create the badge for watchlist
	https://betterprogramming.pub/django-quick-tips-context-processors-da74f887f1fc
	"""
	watch_count = 0
	listings = Listing.objects.all()
	for listing in listings: 
		# Check if user is watching listing
		if request.user in listing.watchlist.all():
			# Increment watch_count
			watch_count += 1
	return {
		"watch_count":watch_count
	}
	