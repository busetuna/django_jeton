from django.contrib import admin
from django.urls import path
from uygulama_adi import views as uygulama_views 
from kbkmarket import views as kbkmarket_views 
from match import views as match_views  

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', uygulama_views.scrape_data, name='home'),  
    path('scrape/', uygulama_views.scrape_data, name='scrape_data'), 
    path('kbkmarket/', kbkmarket_views.scrape_kbkmarket, name='scrape_kbkmarket'), 
    path('match/', match_views.match_products, name='match_products'), 
]
