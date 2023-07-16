from django.urls import path
from dashboard.views import Home, DashboardView, DashboardOrderView, ChangeOrderStatusView, AddToBillView
from dashboard.consumers import OrderConsumer

app_name="dashboard"

urlpatterns = [
    path('', Home.as_view(), name="home"),
    path('restaurant/<int:restaurant_pk>/', DashboardView.as_view(), name='restaurant_dashboard'),
    path('restaurant/order/<int:pk>/', DashboardOrderView.as_view(), name='order_dashboard'),
    path('restaurant/order/<int:pk>/change/status/', ChangeOrderStatusView.as_view(), name='order_status_change'),
    path('restaurant/order/<int:pk>/add_to_bill/', AddToBillView.as_view(), name='order_add_to_bill'),
]

websocket_urlpatterns = [
    path('orders/<int:restaurant_pk>/', OrderConsumer.as_asgi()),
]
