from django.urls import path
from settings.views import Home, RestaurantSettings

app_name = 'settings'

urlpatterns = [
    path('', Home.as_view(), name='home'),
    path('restaurant/<int:pk>', RestaurantSettings.as_view(), name='restaurant_settings')
]
