import urllib.parse
import uuid
from django.db import models


class Category(models.Model):
  name = models.CharField(
      max_length=100, help_text="e.g., 'Mug Printing' or 'Photo Framing'"
  )
  slug = models.SlugField(
      max_length=100, unique=True, help_text="e.g., 'mugs' or 'photos'"
  )
  description = models.TextField(blank=True, null=True)
  icon_emoji = models.CharField(max_length=10, default='🎨')
  created_at = models.DateTimeField(auto_now_add=True)

  class Meta:
    verbose_name_plural = 'Categories'
    ordering = ['name']

  def __str__(self):
    return self.name


class TemplateCategory(models.Model):
  name = models.CharField(max_length=100)
  slug = models.SlugField(max_length=100, unique=True)
  target_category = models.ForeignKey(
      Category,
      on_delete=models.CASCADE,
      related_name='template_categories',
      null=True,
      blank=True,
  )
  description = models.TextField(blank=True, null=True)

  class Meta:
    verbose_name_plural = 'Template Categories'

  def __str__(self):
    target = self.target_category.name if self.target_category else 'All'
    return f'{self.name} ({target})'


class DesignTemplate(models.Model):
  title = models.CharField(max_length=150)
  template_code = models.CharField(max_length=50, unique=True)
  category = models.ForeignKey(
      TemplateCategory, on_delete=models.CASCADE, related_name='templates'
  )
  preview_image = models.ImageField(upload_to='studio/templates/')
  required_photos = models.PositiveIntegerField(default=1)
  is_active = models.BooleanField(default=True)
  created_at = models.DateTimeField(auto_now_add=True)

  def __str__(self):
    return f'[{self.template_code}] {self.title}'


class StudioItem(models.Model):
  title = models.CharField(max_length=200)
  category = models.ForeignKey(
      Category,
      on_delete=models.CASCADE,
      related_name='items',
      null=True,
      blank=True,
  )
  base_price = models.DecimalField(max_digits=10, decimal_places=2)
  featured_image = models.ImageField(upload_to='studio/items/')
  description = models.TextField()
  is_available = models.BooleanField(default=True)
  created_at = models.DateTimeField(auto_now_add=True)

  def __str__(self):
    return f'{self.title} - LKR {self.base_price}'


class StudioOrder(models.Model):
  ORDER_MODE_CHOICES = [
      ('template', 'Pre-Built Design Template'),
      ('custom', 'Custom Design Request (+ LKR 300)'),
  ]

  DELIVERY_CHOICES = [
      ('courier', 'Islandwide Courier (+ LKR 400)'),
      ('pickup', 'Self Pickup (Free)'),
  ]

  STATUS_CHOICES = [
      ('pending', 'Pending Payment'),
      ('confirmed', 'Payment Confirmed'),
      ('proofing', 'Proofing Ready'),
      ('printing', 'In Printing Queue'),
      ('dispatched', 'Dispatched / Ready for Pickup'),
  ]

  order_number = models.CharField(max_length=20, unique=True, editable=False)
  item = models.ForeignKey(
      StudioItem, on_delete=models.CASCADE, related_name='orders'
  )
  order_mode = models.CharField(
      max_length=20, choices=ORDER_MODE_CHOICES, default='template'
  )
  selected_template = models.ForeignKey(
      DesignTemplate, on_delete=models.SET_NULL, null=True, blank=True
  )

  customer_name = models.CharField(max_length=150)
  whatsapp_number = models.CharField(max_length=20)
  delivery_type = models.CharField(
      max_length=20, choices=DELIVERY_CHOICES, default='courier'
  )
  delivery_address = models.TextField(blank=True, null=True)
  custom_text = models.TextField(max_length=300, blank=True, null=True)

  photo_1 = models.ImageField(
      upload_to='studio/orders/%Y/%m/', blank=True, null=True
  )
  photo_2 = models.ImageField(
      upload_to='studio/orders/%Y/%m/', blank=True, null=True
  )
  photo_3 = models.ImageField(
      upload_to='studio/orders/%Y/%m/', blank=True, null=True
  )
  photo_4 = models.ImageField(
      upload_to='studio/orders/%Y/%m/', blank=True, null=True
  )
  photo_5 = models.ImageField(
      upload_to='studio/orders/%Y/%m/', blank=True, null=True
  )
  photo_6 = models.ImageField(
      upload_to='studio/orders/%Y/%m/', blank=True, null=True
  )
  photo_count = models.PositiveIntegerField(default=1)

  quantity = models.PositiveIntegerField(default=1)
  custom_design_fee = models.DecimalField(
      max_digits=10, decimal_places=2, default=0.00
  )
  extra_photo_fee = models.DecimalField(
      max_digits=10, decimal_places=2, default=0.00
  )
  delivery_fee = models.DecimalField(
      max_digits=10, decimal_places=2, default=400.00
  )
  total_amount = models.DecimalField(max_digits=10, decimal_places=2)

  status = models.CharField(
      max_length=20, choices=STATUS_CHOICES, default='pending'
  )
  created_at = models.DateTimeField(auto_now_add=True)

  def save(self, *args, **kwargs):
    if not self.order_number:
      loop_count = 0
      while True:
        candidate_ref = f'DG-{uuid.uuid4().hex[:6].upper()}'
        if not StudioOrder.objects.filter(order_number=candidate_ref).exists():
          self.order_number = candidate_ref
          break
        loop_count += 1
        if loop_count > 50:
          self.order_number = f'DG-{uuid.uuid4().hex[:8].upper()}'
          break
    super().save(*args, **kwargs)

  def _clean_phone_number(self):
    clean_phone = (
        self.whatsapp_number.replace('+', '').replace(' ', '').replace('-', '')
    )
    if clean_phone.startswith('0'):
      clean_phone = '94' + clean_phone[1:]
    return clean_phone

  def generate_proof_whatsapp_link(self):
    msg = (
        f'Hi {self.customer_name}! Here is your print proof for Order'
        f' #{self.order_number}.\nItem: {self.item.title}\n\nPlease reply YES to'
        ' approve for printing!'
    )
    clean_phone = self._clean_phone_number()
    return f'https://wa.me/{clean_phone}?text={urllib.parse.quote(msg)}'

  def get_status_whatsapp_link(self):
    tracking_url = f'http://localhost:8000/studio/track/?ref={self.order_number}&phone={self.whatsapp_number}'
    msg = (
        f'Hello {self.customer_name}! Update on Order #{self.order_number}:'
        f' {self.get_status_display()}.\nTrack progress here: {tracking_url}'
    )
    clean_phone = self._clean_phone_number()
    return f'https://wa.me/{clean_phone}?text={urllib.parse.quote(msg)}'

  def __str__(self):
    return f'Order {self.order_number} - {self.customer_name}'