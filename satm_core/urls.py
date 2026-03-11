from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView, RedirectView

# Admin branding
admin.site.site_header = 'SATM Admin'
admin.site.site_title = 'SATM Administration'
admin.site.index_title = 'SATM Management Dashboard'

urlpatterns = [
    path('satm-admin/', admin.site.urls),
    path('accounts/login/', RedirectView.as_view(pattern_name='login', permanent=False)),
    path('', TemplateView.as_view(template_name='home.html'), name='home'),
    path('', include('users.urls')), 
]

from django.conf import settings
from django.conf.urls.static import static

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

