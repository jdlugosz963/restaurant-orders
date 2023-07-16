from django.db import models
from django.contrib.auth.models import User
from django.shortcuts import Http404, get_object_or_404

from datetime import datetime


class Restaurant(models.Model):
    name = models.CharField(max_length=50)
    users = models.ManyToManyField(User)

    wordpress_url = models.URLField(max_length=50, unique=True)
    woocommerce_consumer_key = models.CharField(max_length=50)
    woocommerce_consumer_secret = models.CharField(max_length=50)
    woocommerce_webhook_secret = models.CharField(max_length=50)

    @classmethod
    def get_user_restaurants(cls, user: User):
        return cls.objects.filter(users=user)

    @classmethod
    def get_user_restaurant_or_404(cls, pk, user: User):
        return get_object_or_404(cls, pk=pk, users=user)

    def __str__(self):
        return self.name


class Order(models.Model):
    WP_STATES = (
        ('pending', 'Oczekujace'),
        ('processing', 'Przetwarzane'),
        ('on-hold', 'Wstrzymane'),
        ('completed', 'Zakonczone'),
        ('cancelled', 'Anulowane'),
        ('refunded', 'Zwrocone'),
        ('failed', 'Nie powiodlo sie'),
        ('trash', 'Usuniete')
    )

    wp_id = models.IntegerField(editable=False)
    wp_status = models.CharField(max_length=30, choices=WP_STATES)
    wp_order_key = models.CharField(max_length=50, editable=False)
    date_created = models.DateField(editable=False)
    date_modified = models.DateField()
    line_items = models.JSONField()
    billing = models.JSONField()
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE)
    can_display = models.BooleanField(default=True)

    @classmethod
    def update_or_create_from_response(cls, response, restaurant_model):
        try:
            obj = cls.objects.update_or_create(
                wp_id=response['id'],
                wp_order_key=response['order_key'],
                restaurant=restaurant_model,
                defaults={
                    'wp_status': response['status'],
                    'date_created': datetime.strptime(response['date_created'], '%Y-%m-%dT%H:%M:%S'),
                    'date_modified': datetime.strptime(response['date_modified'], '%Y-%m-%dT%H:%M:%S'),
                    'line_items': response['line_items'],
                    'billing': response['billing'],
                }
            )
            return obj
        except KeyError:
            return None


    @classmethod
    def create_from_response_disable_view(cls, response, restaurant_model):
        obj, _ = cls.update_or_create_from_response(response, restaurant_model)
        obj.can_display = False
        obj.save()
        return obj

    @classmethod
    def get_order(cls, pk, user: User):
        try:
            return cls.objects.get(
                pk=pk,
                can_display=True,
                restaurant__users=user
            )
        except cls.DoesNotExist:
            raise Http404

    def __str__(self):
        return f'{self.wp_order_key} - {self.date_created}'
