import csv
import datetime

from django.contrib import admin
from django.http import HttpResponse
from django.urls import reverse
from django.utils.safestring import mark_safe

from shop.MessageSender import MessageSender
from shop.models import Message
from .models import Order, OrderItem


def export_to_csv(modeladmin, request, queryset):
    opts = modeladmin.model._meta
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename={}.csv'.format(opts.verbose_name)
    writer = csv.writer(response)

    fields = [field for field in opts.get_fields() if not field.many_to_many and not field.one_to_many]
    writer.writerow([field.verbose_name for field in fields])
    for obj in queryset:
        data_row = []
        for field in fields:
            value = getattr(obj, field.name)
            if isinstance(value, datetime.datetime):
                value = value.strftime('%d/%m/%Y')
            data_row.append(value)
        writer.writerow(data_row)
    return response


export_to_csv.short_description = 'Export to CSV'


def order_detail(obj):
    return mark_safe('<a href="{}">View</a>'.format(reverse('orders:admin_order_detail', args=[obj.id])))


# order_detail.allow_tags=True

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    raw_id_fields = ['product']


class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'first_name', 'last_name', 'email', 'phone', 'address', 'postal_code', 'city', 'created',
                    'updated',
                    'paid', 'paid_by', 'total', 'shipped', order_detail]
    list_filter = ['paid', 'paid_by', 'created', 'updated']
    list_editable = ['shipped']
    inlines = [OrderItemInline]
    actions = [export_to_csv]

    def save_model(self, request, obj, form, change):
        field = 'shipped'
        super().save_model(request, obj, form, change)
        if change and field in form.changed_data and form.cleaned_data.get(field):
            order = Order.objects.prefetch_related('items').filter(id=obj.id)
            if order[0].delivery_type != 'Személyes átvétel':
                subject = f'Csomag feladva #{str(order[0].id)}'
                result, msg = MessageSender(subject=subject, to=order[0].email,
                                            sender='www.minervastudio.hu').send_shipping_confirmation_email(
                    {'name': order[0].full_name})
                sent = True if result == 1 else False
                Message.objects.create(subject=subject, email=order[0].email, message=msg,
                                       sender='System message from Minerva Studio', sent=sent)


admin.site.register(Order, OrderAdmin)
