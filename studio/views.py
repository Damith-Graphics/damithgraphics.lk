from decimal import Decimal
import urllib.parse
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Q, Sum
from django.shortcuts import get_object_or_404, redirect, render

from .models import Category, DesignTemplate, StudioItem, StudioOrder, TemplateCategory


def studio_home(request):
  categories = Category.objects.all()
  return render(request, 'studio/index.html', {'categories': categories})


def studio_showcase(request, category):
    category_obj = get_object_or_404(Category, slug=category)
    items = StudioItem.objects.filter(category=category_obj, is_available=True)
    return render(
        request,
        'studio/showcase.html',
        {
            'category': category_obj,
            'title': category_obj.name,
            'items': items,
        },
    )


def create_order(request, item_id):
  item = get_object_or_404(StudioItem, id=item_id, is_available=True)
  template_categories = TemplateCategory.objects.filter(
      Q(target_category=item.category) | Q(target_category__isnull=True)
  ).prefetch_related('templates')

  if request.method == 'POST':
    order_mode = request.POST.get('order_mode', 'template')
    template_id = request.POST.get('selected_template')
    customer_name = request.POST.get('customer_name', '').strip()
    whatsapp_number = request.POST.get('whatsapp_number', '').strip()
    delivery_type = request.POST.get('delivery_type', 'courier')
    delivery_address = request.POST.get('delivery_address', '').strip()
    custom_text = request.POST.get('custom_text', '').strip()

    # Server-Side Input Validation
    try:
      quantity = int(request.POST.get('quantity', 1))
      if quantity < 1:
        quantity = 1
    except (ValueError, TypeError):
      quantity = 1

    selected_template = None
    if order_mode == 'template' and template_id:
      selected_template = DesignTemplate.objects.filter(
          id=template_id
      ).first()

    # Collect and validate uploaded photos
    uploaded_photos = []
    allowed_extensions = ['.jpg', '.jpeg', '.png', '.webp']
    for i in range(1, 7):
      photo = request.FILES.get(f'photo_{i}')
      if photo:
        ext = photo.name.lower().split('.')[-1]
        if f'.{ext}' in allowed_extensions and photo.size <= 15 * 1024 * 1024:
            uploaded_photos.append(photo)
    photo_count = max(len(uploaded_photos), 1)

    # Server-Side Pricing Calculation
    base_item_total = item.base_price * quantity
    custom_design_fee = (
        Decimal('300.00') if order_mode == 'custom' else Decimal('0.00')
    )
    extra_photo_fee = (
        Decimal('200.00') if photo_count > 4 else Decimal('0.00')
    )
    delivery_fee = (
        Decimal('400.00') if delivery_type == 'courier' else Decimal('0.00')
    )

    total_amount = (
        base_item_total + custom_design_fee + extra_photo_fee + delivery_fee
    )

    order = StudioOrder.objects.create(
        item=item,
        order_mode=order_mode,
        selected_template=selected_template,
        customer_name=customer_name or 'Customer',
        whatsapp_number=whatsapp_number or '0770000000',
        delivery_type=delivery_type,
        delivery_address=delivery_address,
        custom_text=custom_text,
        quantity=quantity,
        photo_count=photo_count,
        custom_design_fee=custom_design_fee,
        extra_photo_fee=extra_photo_fee,
        delivery_fee=delivery_fee,
        total_amount=total_amount,
        photo_1=uploaded_photos[0] if len(uploaded_photos) >= 1 else None,
        photo_2=uploaded_photos[1] if len(uploaded_photos) >= 2 else None,
        photo_3=uploaded_photos[2] if len(uploaded_photos) >= 3 else None,
        photo_4=uploaded_photos[3] if len(uploaded_photos) >= 4 else None,
        photo_5=uploaded_photos[4] if len(uploaded_photos) >= 5 else None,
        photo_6=uploaded_photos[5] if len(uploaded_photos) >= 6 else None,
    )

    return redirect(
        'studio:order_confirmation', order_number=order.order_number
    )

  return render(
      request,
      'studio/order_form.html',
      {
          'item': item,
          'template_categories': template_categories,
      },
  )


def order_confirmation(request, order_number):
  order = get_object_or_404(StudioOrder, order_number=order_number)

  wa_message = (
      f'Hello Damith Studio! I placed an order.\n\n'
      f'Order Ref: {order.order_number}\n'
      f'Item: {order.item.title} (x{order.quantity})\n'
      f'Name: {order.customer_name}\n'
      f'Total Payable: LKR {order.total_amount:,.2f}\n\n'
      f'I will attach my payment proof here.'
  )

  studio_whatsapp = '94771234567'
  wa_link = f'https://wa.me/{studio_whatsapp}?text={urllib.parse.quote(wa_message)}'

  return render(
      request,
      'studio/order_confirmation.html',
      {
          'order': order,
          'wa_link': wa_link,
      },
  )


def track_order(request):
  order_ref = request.GET.get('ref', '').strip().upper()
  phone_input = request.GET.get('phone', '').strip()
  order = None
  error = None

  if order_ref or phone_input:
    if not (order_ref and phone_input):
      error = (
          'Security Notice: Please enter BOTH your Order Reference (e.g.,'
          ' DG-A1B2C3) AND your registered WhatsApp phone number to view tracking'
          ' details.'
      )
    else:
      clean_phone = (
          phone_input.replace('+', '').replace(' ', '').replace('-', '')
      )
      if clean_phone.startswith('0'):
        clean_phone = '94' + clean_phone[1:]

      order = StudioOrder.objects.filter(
          order_number__iexact=order_ref, whatsapp_number__icontains=clean_phone
      ).first()

      if not order:
        error = (
            'No matching order found. Please verify your reference number and'
            ' registered phone number.'
        )

  return render(
      request,
      'studio/track_order.html',
      {
          'order': order,
          'order_ref': order_ref,
          'phone_input': phone_input,
          'error': error,
      },
  )


@staff_member_required
def admin_dashboard(request):
  status_filter = request.GET.get('status', '')
  search_query = request.GET.get('q', '').strip()

  orders = StudioOrder.objects.all().select_related('item', 'selected_template')

  if status_filter:
    orders = orders.filter(status=status_filter)

  if search_query:
    orders = orders.filter(
        Q(order_number__icontains=search_query)
        | Q(customer_name__icontains=search_query)
        | Q(whatsapp_number__icontains=search_query)
    )

  # Total revenue calculated strictly for confirmed/completed orders
  total_revenue = orders.filter(
      status__in=['confirmed', 'proofing', 'printing', 'dispatched']
  ).aggregate(Sum('total_amount'))['total_amount__sum'] or Decimal('0.00')

  context = {
      'orders': orders[:100],
      'total_revenue': total_revenue,
      'pending_count': StudioOrder.objects.filter(status='pending').count(),
      'printing_count': StudioOrder.objects.filter(status='printing').count(),
      'completed_count': StudioOrder.objects.filter(
          status='dispatched'
      ).count(),
      'current_filter': status_filter,
      'search_query': search_query,
  }

  return render(request, 'studio/dashboard.html', context)


@staff_member_required
def update_order_status(request, order_id):
  if request.method == 'POST':
    order = get_object_or_404(StudioOrder, id=order_id)
    new_status = request.POST.get('status')
    if new_status in dict(StudioOrder.STATUS_CHOICES):
      order.status = new_status
      order.save()
  return redirect('studio:admin_dashboard')