"""djangoTrade URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls import url, include
from django.conf.urls.static import static
from django.contrib import admin
from trade import views as tradeViews
from allauth import urls as allauth_urls
from user_profile import views as user_profile_views

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^accounts/', include(allauth_urls)),
    url(r'^profile/$', user_profile_views.profile, name='user_profile'),
    url(r'^change_status/$', tradeViews.change_status, name='change_status'),
    url(r'^index/$', tradeViews.index, name='index'),
    url(r'^exchange/$', tradeViews.exchange, name='exchange'),
    url(r'^wallet/$', tradeViews.wallet, name='wallet'),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)


