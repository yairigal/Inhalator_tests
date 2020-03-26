"""air_to_breath2 URL Configuration."""
from django.conf.urls import include, url
from django.contrib import admin


admin.autodiscover()


urlpatterns = [
    url(r'^admin/',admin.site.urls),
    url(r'^rotest/api/', include("rotest.api.urls")),
]
