from django.shortcuts import render
from .models import PortfolioProject

def portfolio_lazy_list(request):
    projects = PortfolioProject.objects.filter(is_active=True)[:6]
    return render(request, 'portfolio/partials/project_grid.html', {'projects': projects})