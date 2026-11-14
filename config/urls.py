from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path("__reload__/", include("django_browser_reload.urls")),
    path('studio/', include('studio.urls', namespace='studio')),  # <--- Added studio route
    path('', include('core.urls')),
    path('', include('portfolio.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])



# Customize Admin Site Headers
admin.site.site_header = "Damith Graphics Admin"
admin.site.site_title = "Damith Graphics Portal"
admin.site.index_title = "Welcome to Damith Graphics Management"