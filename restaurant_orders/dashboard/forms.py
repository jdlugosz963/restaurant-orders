from django import forms

from core.models import Order


FORM_TAILWIND_CLASSES = 'form-control block w-full px-3 py-1.5 text-base font-normal text-gray-700 bg-white bg-clip-padding border border-solid border-gray-300 rounded transition ease-in-out m-0 focus:text-gray-700 focus:bg-white focus:border-blue-600 focus:outline-none'

class OrderStatusForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ('wp_status', )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['wp_status'].label = 'Przenies do:'

class AddToBillForm(forms.Form):
    send_mail = forms.BooleanField(label='Wyslij maila', initial=False, required=False)
    send_sms = forms.BooleanField(label='Wyslij sms', initial=True, required=False)

    def __init__(self, pk, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        order = Order.get_order(pk, user)

        for item in order.line_items:
            index = item['product_id']
            self.fields[index] = forms.IntegerField(required=False, label=item['name'])

        for index in self.fields.keys():
            self.fields[index].widget.attrs.update({'class': FORM_TAILWIND_CLASSES})
