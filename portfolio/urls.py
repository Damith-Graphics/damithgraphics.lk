from django.urls import path
from . import views

urlpatterns = [
    path('portfolio/load-items/', views.portfolio_lazy_list, name='portfolio_lazy_list'),
]