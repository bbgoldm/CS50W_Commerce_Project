from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
	path("createlisting", views.createlisting, name="createlisting"),
	path("listing/<int:listing_id>", views.listing, name="listing"),
	path("<int:listing_id>/bid", views.bid, name="bid"),
	path("<int:listing_id>/closeauction", views.closeauction, name="closeauction"),
	path("watchlist", views.watchlist, name="watchlist"),
	path("<int:listing_id>/watch", views.watch, name="watch"),
	path("categories", views.categories, name="categories"),
	path("category/<str:category_name>", views.category, name="category"),
	path("<int:listing_id>/comment", views.comment, name="comment")
]
