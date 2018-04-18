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
from ticker_app import views as tickerViews
from allauth import urls as allauth_urls
from user_profile import views as user_profile_views
from django.contrib.auth.decorators import permission_required

urlpatterns = [
                  url(r'^admin/', admin.site.urls),
                  url(r'^accounts/', include(allauth_urls)),
                  url(r'^profile/$', user_profile_views.profile, name='user_profile'),
                  url(r'^change_status/$', permission_required('is_superuser')(tradeViews.change_status),
                      name='change_status'),
                  url(r'^$', tradeViews.index, name='index'),
                  url(r'^exchange/$', permission_required('is_superuser')(tradeViews.exchange), name='exchange'),
                  url(r'^wallet/$', permission_required('is_superuser')(tradeViews.wallet), name='wallet'),
                  url(r'^api/$', tradeViews.get_holding, name='get_holding'),
                  url(r'^transaction/new_comment/$',
                      permission_required('is_superuser')(tradeViews.add_new_transaction_comment), name='new_comment'),
                  url(r'^trade/setup/(?P<pk>[0-9]+)/$', tradeBOTViews.setup, name='tradeBotSetup'),
                  url(r'^trade/addusercoin/$', tradeBOTViews.add_user_pair, name='add_user_pair'),
                  url(r'^trade/changerank/$', tradeBOTViews.change_rank, name='changerank'),
                  url(r'^trade/set_share/$', tradeBOTViews.set_share, name='set_share'),
                  url(r'^trade/set_pair_add/$', tradeBOTViews.set_pair_add, name='set_pair_add'),
                  url(r'^trade/delete_user_pair/$', tradeBOTViews.delete_user_pair, name='delete_user_pair'),
                  url(r'^trade/change_primary_coin/$', tradeBOTViews.change_primary_coin, name='change_primary_coin'),
                  url(r'^trade/change_primary_coin_rank/$', tradeBOTViews.change_primary_coin_rank,
                      name='change_primary_coin_rank'),
                  url(r'^trade/relations/$', tradeBOTViews.relations, name='relations'),
                  url(r'^trade/exchange_script_activity/$', tradeBOTViews.change_user_exchange_script_activity,
                      name='change_user_exchange_script_activity'),
                  url(r'^trade/exchange_depth_to_trade/$', tradeBOTViews.exchange_depth_to_trade,
                      name='exchange_depth_to_trade'),
                  url(r'^trade/get_ticker/$', tickerViews.get_ticker, name='get_ticker'),
                  url(r'^trade/get_new_orders_to_trade/$', tradeBOTViews.get_new_to_trade, name='get_new_to_trade'),
              ] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
