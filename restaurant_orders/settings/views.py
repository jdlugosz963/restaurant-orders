from django.urls import reverse
from django.shortcuts import render, redirect, Http404
from django.views.generic.edit import UpdateView, CreateView, View
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin

from core.models import Restaurant
from settings.forms import RestaurantForm


class Home(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = 'core.change_restaurant'

    def get(self, request):
        if not self.request.user.has_perm('settings.change_restaurant'):
            raise Http404

        redirect_url = 'settings:restaurant_settings'
        restaurants = Restaurant.get_user_restaurants(request.user)

        if len(restaurants) == 1:
            return redirect(redirect_url, pk=restaurants[0].pk)

        return render(request, template_name='restaurants_choice.html', context={
            'title': 'Ustawienia',
            'restaurants': restaurants,
            'redirect_url': redirect_url
        })

class RestaurantSettings(LoginRequiredMixin, SuccessMessageMixin, PermissionRequiredMixin, UpdateView):
    template_name = 'settings/restaurant_settings.html'
    form_class = RestaurantForm
    model = Restaurant
    success_message = 'Zapisano!'
    permission_required = 'core.change_restaurant'

    def get_queryset(self, *args, **kwargs):
        return super().get_queryset(*args, **kwargs).filter(
            pk=self.kwargs['pk'],
            users=self.request.user.pk
        )

    def get_success_url(self):
        return reverse('settings:restaurant_settings', args=(self.kwargs['pk'], ))
