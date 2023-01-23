import csv
import datetime
import logging

from django.conf import settings
from django.contrib import admin
from django.contrib import messages
from django.db.models import Count, Sum
from django.http import HttpResponse
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.utils.translation import ngettext

from logs.models import LogFile
from parameters.models import Parameter
from shop.MessageSender import MessageSender
from shop.models import Message
from .models import Order, OrderItem, OrderSummary, OrderItemSummary

log = logging.getLogger(__name__)


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


def re_send_order_email(modeladmin, request, queryset):
    opts = modeladmin.model._meta
    fields = [field for field in opts.get_fields() if not field.many_to_many and not field.one_to_many]
    f = fields
    for obj in queryset:
        data_row = dict()
        for field in fields:
            value = getattr(obj, field.name)
            if isinstance(value, datetime.datetime):
                value = value.strftime('%d/%m/%Y')
            data_row[field.name] = value

        # SEND AN ORDER CONFIRMATION MAIL
        prices = dict(FoxPost=int(Parameter.objects.filter(name="foxpost_price")[0].value),
                      Csomagkuldo=int(Parameter.objects.filter(name="csomagkuldo_price")[0].value),
                      Házhozszállítás=int(Parameter.objects.filter(name="delivery_price")[0].value),
                      Személyesátvétel=0,
                      Ajanlott=int(Parameter.objects.filter(name="ajanlott_price")[0].value))
        o = Order.objects.prefetch_related('items').filter(id=data_row.get("id"))[0]
        order_items = Order.objects.prefetch_related('items').filter(id=data_row.get("id"))[0].items.all()
        order_data = {'Szállítási név': o.delivery_name, 'Szállítási cím': o.address,
                      'Házszám, emelet, ajtó': o.address_number,
                      'Postakód': o.postal_code, 'Település': o.city, 'Megjegyzés': o.note}
        delivery_info = dict(FoxPost={'Átvételi pont': o.fox_post},
                             Csomagkuldo={'Átvételi pont': o.csomagkuldo},
                             Házhozszállítás=order_data,
                             Ajanlott=order_data,
                             Személyesátvétel={'Vezetéknév': o.first_name, 'Keresztnév': o.last_name})
        delivery_price = prices[o.delivery_type.replace(' ', '')]
        delivery_data = delivery_info[o.delivery_type.replace(' ', '')]
        order_total = o.total
        result, msg = MessageSender(subject=f'Rendelés megerősítése #{str(o.id)}', to=o.email,
                                    sender='www.minervastudio.hu').send_order_confirmation_email(
            {'name': o.full_name, 'order': o,
             'delivery_price': delivery_price,
             'delivery_info': delivery_data,
             'order_total': order_total})
        sent = True if result == 1 else False
        Message.objects.create(subject=f'Rendelés megerősítése #{str(o.id)}', email=o.email, message=msg,
                               sender='System message from Minerva Studio', sent=sent)
        # SEND EMAIL ABOUT THE ORDER
        product = ', '.join([i.product.name for i in order_items])
        msg = f'Új rendelés:\nA rendelés száma: #{str(o.id)}\nA rendelés összege: {str(order_total)} Ft\nTermékek: {product}'
        result = MessageSender(subject=f'Új rendelés #{str(o.id)}', to=settings.EMAIL_HOST_USER,
                               sender='www.minervastudio.hu',
                               message=msg).send_mail()
        sent = True if result == 1 else False
        LogFile.objects.create(type='INFO', message=f'Message is sent to "{o.email}", status: "{result}"')
        Message.objects.create(subject=f'Új rendelés #{str(o.id)}', email=settings.EMAIL_HOST_USER, message=msg,
                               sender='System message from Minerva Studio', sent=sent)


re_send_order_email.short_description = 'Resend Order Email'


def _send_message(order):
    subject = f'Csomag feladva #{str(order.id)}'
    result, msg = MessageSender(subject=subject, to=order.email,
                                sender='www.minervastudio.hu').send_shipping_confirmation_email(
        {'name': order.full_name})
    sent = True if result == 1 else False
    Message.objects.create(subject=subject, email=order.email, message=msg,
                           sender='System message from Minerva Studio', sent=sent)


def shipping(modeladmin, request, queryset):
    updates = 0
    for order in queryset:
        log.info(f'Saving order #{order.id} from admin page, shipped is set to true')
        if order.delivery_type != 'Személyes átvétel':
            order.shipped = True
            order.save()
            log.info(f'Sending message to: {order.email}')
            _send_message(order)
            updates += 1
    orders = ", ".join([str(q.id) for q in queryset])
    singular = f'%d order ({orders}) was successfully marked as shipped.'
    plural = f'%d orders ({orders}) were successfully marked as shipped.'
    modeladmin.message_user(request, ngettext(singular, plural, updates, ) % updates, messages.SUCCESS)


shipping.short_description = 'Set Order to be shipped'


def order_detail(obj):
    return mark_safe('<a href="{}">View</a>'.format(reverse('orders:admin_order_detail', args=[obj.id])))


def show_product(obj):
    return mark_safe('<a target="_blank" href="/termek/{}/{}">Product</a>'
                     .format(obj.product.collection.slug, obj.product.slug))


# order_detail.allow_tags=True

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    raw_id_fields = ['product']
    readonly_fields = ['id', 'product', 'price', 'quantity', 'color', 'stud', 'finding', 'first_initial',
                       'second_initial',
                       'custom_date', show_product]
    exclude = ['gift_card', 'image']
    can_delete = False

    # @admin.display(description='gift_card')
    # def gift_card_name(self, instance):
    #     return instance.name

    def has_add_permission(self, request, obj):
        return False


class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'first_name', 'last_name', 'email', 'phone', 'address',
                    'postal_code', 'city', 'created', 'updated', 'paid', 'paid_by', 'total', 'shipped']
    list_filter = ['paid', 'paid_by', 'created', 'updated']
    fieldsets = (
        ('Kötelező mezők', {
            'fields': ('full_name', 'phone', 'email', 'billing_address', 'billing_address_number',
                       'billing_postal_code', 'billing_city', 'product_note',)
        }),
        ('Szállítás módja', {
            'fields': ('delivery_type',)
        }),
        ('Személyes átvétel', {
            'fields': ('first_name', 'last_name',)
        }),
        ('Foxpost', {
            'fields': ('fox_post',)
        }),
        ('Csomagküldő', {
            'fields': ('csomagkuldo',)
        }),
        ('Házhozszállítás', {
            'fields': ('delivery_name', 'address', 'address_number', 'postal_code', 'city', 'note',)
        }),
        ('Ár', {
            'fields': ('products_price', 'products_price_with_discount', 'delivery_cost', 'subtotal', 'total',)
        }),
        ('Kupon', {
            'fields': ('coupon', 'discount', 'discount_amount',)
        }),
        ('Fizetési részletek', {
            'fields': ('paid', 'paid_time', 'shipped',)
        })
    )
    readonly_fields = ('full_name', 'phone', 'email', 'billing_address', 'billing_address_number',
                       'billing_postal_code', 'billing_city', 'product_note', 'delivery_type', 'first_name',
                       'last_name', 'fox_post', 'csomagkuldo', 'delivery_name', 'address', 'address_number',
                       'postal_code', 'city', 'note', 'products_price', 'products_price_with_discount',
                       'delivery_cost', 'subtotal', 'total', 'coupon', 'discount', 'discount_amount',
                       'paid', 'paid_time', 'shipped',)
    list_editable = ['shipped']
    inlines = [OrderItemInline]
    actions = [export_to_csv, re_send_order_email, shipping]

    def render_change_form(self, request, context, add=False, change=False, form_url='', obj=None):
        context.update({
            'show_save_and_add_another': False,
            'show_save': False,
            'show_save_and_continue': False,
            'show_delete': False
        })
        return super().render_change_form(request, context, add, change, form_url, obj)


admin.site.register(Order, OrderAdmin)


@admin.register(OrderSummary)
class OrderSummaryAdmin(admin.ModelAdmin):
    change_list_template = 'admin/orders/order_summary_change_list.html'
    date_hierarchy = 'created'

    # list_filter = (
    #     '',
    # )

    def changelist_view(self, request, extra_context=None):
        response = super().changelist_view(
            request,
            extra_context=extra_context,
        )
        try:
            qs = response.context_data['cl'].queryset.filter(paid=True)
        except (AttributeError, KeyError):
            return response

        metrics = {
            'total': Count('id'),
            'total_product_price': Sum('products_price'),
            'total_delivery_price': Sum('delivery_cost'),
            'total_discount_amount': Sum('discount_amount'),
        }
        response.context_data['summary'] = list(
            qs
                .values('full_name')
                .annotate(**metrics)
                .order_by('-total_product_price')
        )

        response.context_data['summary_total'] = dict(
            qs.aggregate(**metrics)
        )

        return response


@admin.register(OrderItemSummary)
class OrderItemSummaryAdmin(admin.ModelAdmin):
    change_list_template = 'admin/orders/order_item_summary_change_list.html'
    date_hierarchy = 'order__created'

    def changelist_view(self, request, extra_context=None):
        response = super().changelist_view(
            request,
            extra_context=extra_context,
        )
        try:
            qs = response.context_data['cl'].queryset.filter(order__paid=True)
        except (AttributeError, KeyError):
            return response

        metrics = {
            'total': Count('id'),
        }

        response.context_data['summary'] = list(
            qs
                .values('product__name')
                .annotate(**metrics)
                .order_by('-total')
        )

        response.context_data['summary_total'] = dict(
            qs.aggregate(**metrics)
        )

        return response
