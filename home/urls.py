from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("pnl/", views.profit_data, name="pnl"),
    path("next/", views.index, name="index"),
]
