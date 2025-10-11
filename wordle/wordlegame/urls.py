from django.urls import path
from . import views

urlpatterns = [
    path("home/", views.home, name = "home"),
    path("instructions/", views.instructions, name = "instructions"),
    path("game/", views.game, name = "game"),
    path("results/", views.results, name = "results"), 
]