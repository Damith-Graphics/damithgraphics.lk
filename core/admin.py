from django.contrib import admin
from .models import ClientReview

@admin.register(ClientReview)
class ClientReviewAdmin(admin.ModelAdmin):
    list_display = ('client_name', 'client_company_or_project', 'rating', 'is_approved', 'is_submitted', 'created_at')
    list_filter = ('rating', 'is_approved', 'is_submitted')
    search_fields = ('client_name', 'comment')