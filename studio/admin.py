from django.contrib import admin
from django.utils.html import format_html
from .models import Category, DesignTemplate, StudioItem, StudioOrder, TemplateCategory


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
  list_display = ('name', 'slug', 'icon_emoji', 'created_at')
  prepopulated_fields = {'slug': ('name',)}
  search_fields = ('name', 'slug')


@admin.register(TemplateCategory)
class TemplateCategoryAdmin(admin.ModelAdmin):
  list_display = ('name', 'slug', 'target_category')
  list_filter = ('target_category',)
  prepopulated_fields = {'slug': ('name',)}
  search_fields = ('name',)


@admin.register(DesignTemplate)
class DesignTemplateAdmin(admin.ModelAdmin):
  list_display = (
      'template_code',
      'title',
      'category',
      'required_photos',
      'is_active',
  )
  list_filter = ('category__target_category', 'is_active')
  search_fields = ('template_code', 'title')


@admin.register(StudioItem)
class StudioItemAdmin(admin.ModelAdmin):
  list_display = (
      'title',
      'category',
      'base_price',
      'is_available',
      'created_at',
  )
  list_filter = ('category', 'is_available')
  search_fields = ('title', 'description')


@admin.register(StudioOrder)
class StudioOrderAdmin(admin.ModelAdmin):
  list_display = (
      'order_number',
      'item',
      'order_mode',
      'selected_template',
      'customer_name',
      'whatsapp_number',
      'photo_count',
      'total_amount',
      'status',
      'send_whatsapp_status',
      'send_whatsapp_proof',
  )
  list_filter = ('status', 'order_mode', 'delivery_type', 'created_at')
  search_fields = ('order_number', 'customer_name', 'whatsapp_number')
  readonly_fields = (
      'order_number',
      'custom_design_fee',
      'extra_photo_fee',
      'delivery_fee',
      'total_amount',
      'created_at',
  )

  def send_whatsapp_status(self, obj):
    link = obj.get_status_whatsapp_link()
    return format_html(
        '<a class="button" href="{}" target="_blank" style="background-color:'
        ' #F59E0B; color: #000; font-weight: bold; border-radius:'
        ' 6px;">Status WA</a>',
        link,
    )

  send_whatsapp_status.short_description = 'Notify Status'

  def send_whatsapp_proof(self, obj):
    link = obj.generate_proof_whatsapp_link()
    return format_html(
        '<a class="button" href="{}" target="_blank" style="background-color:'
        ' #25D366; color: white; font-weight: bold; border-radius:'
        ' 6px;">Proof WA</a>',
        link,
    )

  send_whatsapp_proof.short_description = 'Send Proof'