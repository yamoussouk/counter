import csv
import datetime

from django.contrib import admin
from django.db.models import Count, Sum
from django.http import HttpResponse
from django.urls import reverse
from django.utils.safestring import mark_safe

from shop.MessageSender import MessageSender
from shop.models import Message
from .models import Order, OrderItem, OrderSummary, OrderItemSummary


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


def show_product(obj):
    return mark_safe('<a target="_blank" href="/termek/{}/{}">Product</a>'
                     .format(obj.product.collection.slug, obj.product.slug))


# order_detail.allow_tags=True

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    raw_id_fields = ['product']
    readonly_fields = ['id', 'product', 'price', 'quantity', 'color', 'stud', 'first_initial', 'second_initial',
                       'custom_date', show_product]
    exclude = ['gift_card', 'image']
    can_delete = False

    def has_add_permission(self, request, obj):
        return False


class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'first_name', 'last_name', 'email', 'phone', 'address', 'postal_code', 'city', 'created',
                    'updated', 'paid', 'paid_by', 'total', 'shipped']
    list_filter = ['paid', 'paid_by', 'created', 'updated']
    fieldsets = (
        ('Kötelező mezők', {
            'fields': ('full_name', 'phone', 'email', 'billing_address', 'billing_postal_code', 'billing_city',
                       'product_note',)
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
            'fields': ('delivery_name', 'address', 'postal_code', 'city', 'note',)
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
    readonly_fields = ('full_name', 'phone', 'email', 'billing_address', 'billing_postal_code', 'billing_city',
                       'product_note', 'delivery_type', 'first_name', 'last_name', 'fox_post', 'csomagkuldo',
                       'delivery_name', 'address', 'postal_code', 'city', 'note', 'products_price',
                       'products_price_with_discount', 'delivery_cost', 'subtotal', 'total', 'coupon', 'discount',
                       'discount_amount', 'paid', 'paid_time', 'shipped',)
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
            qs = response.context_data['cl'].queryset
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
            qs = response.context_data['cl'].queryset
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
