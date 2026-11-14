import uuid
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

class ClientReview(models.Model):
    client_name = models.CharField(max_length=150)
    client_company_or_project = models.CharField(max_length=200, blank=True, help_text="e.g. SP Residential")
    rating = models.PositiveIntegerField(
        default=5, 
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    comment = models.TextField(max_length=1000)
    is_approved = models.BooleanField(default=True, help_text="Toggle to show on homepage")
    
    # Token for secure single-use submission link
    access_token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    is_submitted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.client_name} - {self.rating} Stars"