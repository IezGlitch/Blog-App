
from django.contrib import admin
from django.urls import include,path
from django.views.generic import RedirectView
from django.contrib.sitemaps.views import sitemap
from blog.sitemaps import PostSitemap

sitemaps={'posts':PostSitemap}


urlpatterns = [
    path("", RedirectView.as_view(pattern_name='blog:post_list', permanent=False)),
    path("admin/", admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),
    path('accounts/', include('accounts.urls', namespace='accounts')),
    path('blog/',include('blog.urls',namespace='blog')),
    path('sitemap.xml', sitemap, {'sitemaps':sitemaps},
         name='django.contrib.sitemaps.views.sitemap')]
