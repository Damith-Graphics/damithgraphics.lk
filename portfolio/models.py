import uuid
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

class PortfolioProject(models.Model):
    CATEGORY_CHOICES = [
        ('web', 'Web Development'),
        ('graphic', 'Graphic Design'),
        ('branding', 'Branding & Packaging'),
    ]

    title = models.CharField(max_length=200)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='web')
    featured_image = models.ImageField(upload_to='portfolio/')
    short_description = models.TextField(max_length=300)
    external_url = models.URLField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    # --- CLIENT REVIEW & TESTIMONIAL FIELDS ---
    client_name = models.CharField(max_length=150, blank=True, null=True, help_text="e.g., Sareegalore Team")
    client_comment = models.TextField(max_length=500, blank=True, null=True, help_text="Client feedback / testimonial")
    client_rating = models.PositiveIntegerField(
        default=5,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Rating from 1 to 5 stars"
    )
    
    # Set default=uuid.uuid4 and remove unique constraint for initial migration
    review_token = models.UUIDField(default=uuid.uuid4, editable=False)
    is_review_submitted = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} ({self.get_category_display()})"