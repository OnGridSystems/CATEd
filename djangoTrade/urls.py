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
from tradeBOT import views as tradeBOTViews
from allauth import urls as allauth_urls
from user_profile import views as user_profile_views
from django.contrib.auth.decorators import permission_required


urlpatterns = [
                  url(r'^admin/', admin.site.urls),
                  url(r'^accounts/', include(allauth_urls)),
                  url(r'^profile/$', user_profile_views.profile, name='user_profile'),
                  url(r'^change_status/$', permission_required('is_superuser')(tradeViews.change_status), name='change_status'),
                  url(r'^$', tradeViews.index, name='index'),
                  url(r'^exchange/$', permission_required('is_superuser')(tradeViews.exchange), name='exchange'),
                  url(r'^wallet/$', permission_required('is_superuser')(tradeViews.wallet), name='wallet'),
                  url(r'^api/$', tradeViews.get_holding, name='get_holding'),
                  url(r'^transaction/new_comment/$',
                      permission_required('is_superuser')(tradeViews.add_new_transaction_comment), name='new_comment'),
                  url(r'^trade/$', tradeBOTViews.main, name='tradeBotMain'),
                  url(r'^trade/setup/(?P<pk>[0-9]+)/$', tradeBOTViews.setup, name='tradeBotSetup'),
                  url(r'^trade/addusercoin/$', tradeBOTViews.add_user_coin, name='add_user_coin'),
                  url(r'^trade/changerank/$', tradeBOTViews.changerank, name='changerank'),
                  url(r'^trade/toggle_pair/$', tradeBOTViews.toggle_pair, name='toggle_pair'),
                  url(r'^trade/set_share/$', tradeBOTViews.set_share, name='set_share'),
                  url(r'^trade/delete_user_coin/$', tradeBOTViews.delete_user_coin, name='delete_user_coin'),
                  url(r'^trade/relations/$', tradeBOTViews.relations, name='relations'),
              ] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
