from django.urls import path
from . import views

urlpatterns = [
    path("move/", views.MoveView.as_view()),
    path("offer/", views.ChangeTrainingView.as_view())
]