from django.shortcuts import render, redirect, reverse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.list import ListView, View
from django.views.generic.edit import UpdateView
from django.contrib.messages.views import SuccessMessageMixin
from django.core import serializers
from django.contrib import messages


from dashboard.forms import OrderStatusForm, AddToBillForm
from core.tasks import create_order_and_send_notification
from core.models import Restaurant, Order

class Home(LoginRequiredMixin, View):
    def get(self, request):
        redirect_url = 'dashboard:restaurant_dashboard'
        restaurants = Restaurant.get_user_restaurants(request.user)

        if len(restaurants) == 1:
            return redirect(redirect_url, restaurant_pk=restaurants[0].pk)

        return render(request, template_name='restaurants_choice.html', context={
            'title': 'Dashboard',
            'restaurants': restaurants,
            'redirect_url': redirect_url
        })

class DashboardView(LoginRequiredMixin, ListView):
    template_name = 'dashboard/dashboard.html'
    model = Order
    paginate_by = 4

    def get_queryset(self, *args, **kwargs):
        restaurant = Restaurant.get_user_restaurant_or_404(pk=self.kwargs.get('restaurant_pk'),
                                                           user=self.request.user)

        status = self.request.GET.get('status')
        queryset = {}
        if status:
            queryset['wp_status'] = status

        obj = super().get_queryset(*args, **kwargs).filter(
            restaurant=restaurant,
            can_display=True,
            **queryset
        ).order_by('-wp_id')

        return obj


class DashboardOrderView(LoginRequiredMixin, View):
    def get(self, request, pk):
        order = Order.get_order(pk, request.user)
        orderStatusForm = OrderStatusForm(instance=order)
        addToBillForm = AddToBillForm(pk, request.user)

        return render(request, 'dashboard/dashboard_order.html', context={
            'order': order,
            'orderStatusForm': orderStatusForm,
            'addToBillForm': addToBillForm
        })


class ChangeOrderStatusView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    form_class = OrderStatusForm
    model = Order
    success_message = 'Zapisano!'
    slug_field='order_pk'

    def get_queryset(self, *args, **kwargs):
        return super().get_queryset(*args, **kwargs).filter(
            pk=self.kwargs['pk'],
            can_display=True,
            restaurant__users=self.request.user.pk
        )

    def get_success_url(self):
        return reverse('dashboard:order_dashboard', args=(self.kwargs['pk'], ))

class AddToBillView(LoginRequiredMixin, View):
    def post(self, request, pk, *args, **kwargs):
        addToBillForm = AddToBillForm(pk, request.user, request.POST)

        if addToBillForm.is_valid():
            order = Order.get_order(pk, request.user)
            order = serializers.serialize('json', (order, ))
            email = True if addToBillForm.data.get('send_mail') else False
            phone = True if addToBillForm.data.get('send_sms') else False
            items = [(wp_pk, price) for wp_pk, price in request.POST.items() if price.isdigit()]

            # TODO: Za duzo tych jebanych argumentow !
            create_order_and_send_notification.delay(order, items, email, phone, request.user.pk)


        return redirect('dashboard:order_dashboard', pk)
