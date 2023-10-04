from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    
    path("listings/<int:id>", views.listings, name="listings"),
    path("create", views.create , name="create"),
    
    path("categories", views.categories , name="categories"),
    path("post_category/<int:id>", views.post_category , name="post_category"),

    path("<int:id>", views.watchlist , name="watchlist"),
    path("watchlist", views.watch , name="watch"),
    path("bids/<int:id>", views.post_bid , name="post_bid"),
    path("comments/<int:id>", views.post_comment , name="post_comment"),
    path("closed/<int:id>", views.closed , name="closed"),
]
