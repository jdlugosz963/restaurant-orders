from django import forms
from core.models import Restaurant

FORM_TAILWIND_CLASSES = 'form-control block w-full px-3 py-1.5 text-base font-normal text-gray-700 bg-white bg-clip-padding border border-solid border-gray-300 rounded transition ease-in-out m-0 focus:text-gray-700 focus:bg-white focus:border-blue-600 focus:outline-none'

class RestaurantForm(forms.ModelForm):
    woocommerce_consumer_key = forms.CharField(required=False)
    woocommerce_consumer_secret = forms.CharField(required=False)
    woocommerce_webhook_secret = forms.CharField(required=False)

    class Meta:
        model = Restaurant
        exclude = ('users', )

    def __init__(self, *args, **kwargs):
        super(RestaurantForm, self).__init__(*args, **kwargs)
        for key in self.fields.keys():
            self.fields[key].widget.attrs.update({'class': FORM_TAILWIND_CLASSES})
