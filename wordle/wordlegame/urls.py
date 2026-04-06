from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name = "home"),
    path("home/", views.home, name = "home"),
    path("instructions/", views.instructions, name = "instructions"),
    path("game/", views.game, name = "game"),
    path("agentgame/", views.agentplaygame, name = "agentgame"),
    path("dualgame/", views.dualplaygame, name = "dualgame"),
    path("results/", views.results, name = "results"), 
    path("helpertool/", views.helpertool, name = "helpertool"),
]