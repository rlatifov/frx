from django.urls import path

from frx.pairs.views import HomeView

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
]
