from wordpress_integration.views import webhook
from django.urls import path

app_name = 'wordpress_integration'

urlpatterns = [
    path('<int:restaurant_pk>/', webhook, name='webhook'),
]
