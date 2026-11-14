from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import ClientReview
from studio.models import Category, StudioItem

def index(request):
    """
    Main Index View: Fetches approved client reviews, studio categories,
    and featured items for the main Damith Graphics landing page.
    """
    reviews = ClientReview.objects.filter(is_approved=True, is_submitted=True).order_by('-created_at')[:6]
    categories = Category.objects.all()
    featured_items = StudioItem.objects.filter(is_available=True)[:6]

    context = {
        'reviews': reviews,
        'categories': categories,
        'featured_items': featured_items,
    }
    return render(request, 'core/index.html', context)


def submit_review(request, token):
    """
    Review Submission View: Validates access token and processes user review input safely.
    """
    review = get_object_or_404(ClientReview, access_token=token)

    if review.is_submitted:
        messages.info(request, "Thank you! You have already submitted your review.")
        return redirect('index')

    if request.method == 'POST':
        client_name = request.POST.get('client_name', '').strip()
        rating_raw = request.POST.get('rating', '')
        comment = request.POST.get('comment', '').strip()

        # Input Validation
        if not client_name or not comment or not rating_raw:
            messages.error(request, "Please fill in all required fields before submitting.")
            return render(request, 'core/submit_review.html', {
                'review': review,
                'client_name': client_name,
                'comment': comment,
            })

        # Safe Rating Integer Conversion
        try:
            rating = int(rating_raw)
            if not (1 <= rating <= 5):
                raise ValueError("Rating out of bounds")
        except (ValueError, TypeError):
            messages.error(request, "Please select a valid star rating between 1 and 5.")
            return render(request, 'core/submit_review.html', {
                'review': review,
                'client_name': client_name,
                'comment': comment,
            })

        # Save Review safely
        review.client_name = client_name
        review.rating = rating
        review.comment = comment
        review.is_submitted = True
        review.save()

        messages.success(request, "Your review has been published! Thank you for working with Damith Graphics.")
        return redirect('index')

    return render(request, 'core/submit_review.html', {'review': review})