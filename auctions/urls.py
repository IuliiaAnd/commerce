from django.urls import path

from . import views
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("create_listing/", views.new_listing, name="new_listing"),
    path("listing_page/<int:id>", views.listing_page, name="listing_page"),
    path("watchlist/", views.watchlist_page, name='watchlist'),
    path("add_to_watchlist/<int:id>", views.add_to_watchlist, name="add_to_watchlist"),
    path("remove_from_watchlist/<int:id>", views.remove_from_watchlist, name="remove_from_watchlist"),
    path("add_comment/<int:id>", views.add_comment, name="add_comment"),
    path("categories/", views.category_list, name="category_list"),
    path("categories/<int:category_id>/", views.filter_by_category, name="filter_by_category"),
    path("new_bid/<int:id>", views.new_bid, name='new_bid'),
    path("close_listing/<int:id>", views.close_listing, name='close_listing'),
    path("closed_auctions/", views.closed_auctions, name="closed_auctions"),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)