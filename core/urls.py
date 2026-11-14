from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('review/submit/<uuid:token>/', views.submit_review, name='submit_review'),
]