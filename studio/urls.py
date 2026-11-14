from django.urls import path
from . import views

app_name = 'studio'

urlpatterns = [
    path('', views.studio_home, name='home'),
    path('category/<str:category>/', views.studio_showcase, name='showcase'),
    path('order/<int:item_id>/', views.create_order, name='create_order'),
    path(
        'confirmation/<str:order_number>/',
        views.order_confirmation,
        name='order_confirmation',
    ),
    # Staff Master Dashboard Routes
    path('dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path(
        'dashboard/order/<int:order_id>/update-status/',
        views.update_order_status,
        name='update_order_status',
    ),
    path('track/', views.track_order, name='track_order'),
]