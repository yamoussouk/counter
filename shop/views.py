import os

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.db.utils import OperationalError
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.http import JsonResponse
from django.shortcuts import redirect, reverse
from django.shortcuts import render, get_object_or_404
from django.views.generic.list import ListView

from cart.forms import CartAddProductForm, CartAddCustomProductForm, CartAddGiftCardProductForm
from parameters.models import Parameter
from shop.MessageSender import MessageSender
from .StripeProductGenerator import StripeProductGenerator
from .forms import ContactForm
from .models import Collection, Product, Notification, ProductType, GiftCard, Message

stripe_product_generator = StripeProductGenerator()


def index_hid(request):
    return render(request, 'shop/index.html')


def index(request):
    collections = (Collection.objects.filter(available=True, custom=False, show_on_home_page=True)
                       .order_by('-created')[:9])
    notification = Notification.objects.all()
    return render(request, 'shop/index_hid.html', {'collections': collections, 'notification': notification})


def __get_product_details(request, id: str, slug: str, custom: bool):
    collection = Collection.objects.filter(slug=id)[0]
    product = get_object_or_404(Product, collection=collection, slug=slug, available=True, custom=custom)
    product_types = Product.objects.prefetch_related('product_types').filter(collection=collection, slug=slug,
                                                                             available=True, custom=custom)
    images = Product.objects.prefetch_related('images').filter(collection=collection, slug=slug, available=True,
                                                               custom=custom)
    imgs = images[0].images.all()
    types = product_types[0].product_types.all()
    is_stock = False
    if types:
        for type in types:
            if type.stock > 0:
                is_stock = True
                break
    else:
        if product.stock > 0:
            is_stock = True
    cart_product_form = CartAddCustomProductForm() if custom else CartAddProductForm()
    collections = Collection.objects.filter(available=True, custom=custom).order_by('-created')
    notification = Notification.objects.all()
    collection_slug = product.collection.slug
    view = 'shop:custom_products_view' if custom else 'shop:products_view'
    template = 'shop/product/custom_detail.html' if custom else 'shop/product/detail.html'
    return render(request, template,
                  {'product': product,
                   'notification': notification,
                   'collections': collections,
                   'collection_slug': collection_slug,
                   'types': types,
                   'cart_product_form': cart_product_form,
                   'is_stock': is_stock,
                   'images': imgs,
                   'view': view,
                   'slug': collection_slug
                   })


def product_detail(request, id: str, slug: str):
    return __get_product_details(request, id, slug, False)


def custom_product_detail(request, id: str, slug: str):
    return __get_product_details(request, id, slug, True)


def faq(request):
    foxpost = Parameter.objects.filter(name="foxpost_price")[0].value
    delivery = Parameter.objects.filter(name="delivery_price")[0].value
    csomagkuldo = Parameter.objects.filter(name="csomagkuldo_price")[0].value
    ajanlott = Parameter.objects.filter(name="ajanlott_price")[0].value
    notification = Notification.objects.all()
    return render(request, 'shop/faq.html',
                  {'csomagkuldo': csomagkuldo, 'foxpost': foxpost, 'delivery': delivery,
                   'ajanlott': ajanlott, 'notification': notification})


def contact(request):
    contact_form = ContactForm()
    notification = Notification.objects.all()
    return render(request, 'shop/contact.html', {'contact_form': contact_form, 'notification': notification})


def data_handling(request):
    notification = Notification.objects.all()
    return render(request, 'shop/data_handling.html', {'notification': notification})


def aszf(request):
    notification = Notification.objects.all()
    return render(request, 'shop/aszf.html', {'notification': notification})


def contact_message(request):
    form = ContactForm(request.POST)
    if form.is_valid():
        cd = form.cleaned_data
        subject = cd['subject']
        email = cd['email']
        message = cd['message']
        result = MessageSender('Kapcsolat e-mail a minervastudio.hu oldalról', settings.EMAIL_HOST_USER, email,
                               f'{subject}\n{message}').send_mail()
        sent = True if result == 1 else False
        Message.objects.create(subject=subject, email=email, message=message,
                               sender='System message from Minerva Studio', sent=sent)
        return redirect(reverse('shop:thank_you'))
    else:
        print('error', form.errors.as_data())
        contact_form = ContactForm()
    return render(request, 'shop/contact.html', {'contact_form': contact_form})


def thank_you(request):
    return render(request, 'shop/thank_you.html')


def cookie_consent(request):
    response = HttpResponseRedirect('')
    response.set_cookie('cookie_consent', 'True')
    return response


def impresszum(request):
    notification = Notification.objects.all()
    return render(request, 'shop/impresszum.html', {'notification': notification})


class ProductsView(ListView):
    try:
        collection = None
        model = Product
        paginate_by = 9
        template_name = 'shop/product/list.html'
        context_object_name = 'products'
        stock_dict = dict()
        temp = Product.objects.prefetch_related('product_types').filter(available=True, custom=False)
        for i in temp:
            if len(i.product_types.all()) > 0:
                for h in i.product_types.all().values():
                    if h.get('product_id') not in stock_dict:
                        stock_dict[h.get('product_id')] = int(h.get('stock'))
                    else:
                        stock_dict[h.get('product_id')] += int(h.get('stock'))
            else:
                if i.id not in stock_dict:
                    stock_dict[i.id] = int(i.stock)
                else:
                    stock_dict[i.id] += int(i.stock)
        gift_card = GiftCard.objects.filter(available=True)
        card_gift_cart_product_form = CartAddGiftCardProductForm()
        extra_context = {
            'product_stock': stock_dict,
            'gift_card': gift_card,
            'card_gift_cart_product_form': card_gift_cart_product_form,
            'view': 'shop:products_view'
        }
    except OperationalError:
        pass

    def check_product_stock(self, products) -> dict:
        stock_dict = dict()
        for p in products:
            pr = Product.objects.prefetch_related('product_types').filter(id=p.id, available=True, custom=False)[0]
            if len(pr.product_types.all()) > 0:
                for h in pr.product_types.all().values():
                    if h.get('product_id') not in stock_dict:
                        stock_dict[h.get('product_id')] = int(h.get('stock'))
                    else:
                        stock_dict[h.get('product_id')] += int(h.get('stock'))
            else:
                if pr.id not in stock_dict:
                    stock_dict[pr.id] = int(pr.stock)
                else:
                    stock_dict[pr.id] += int(pr.stock)
        return stock_dict

    def get_queryset(self):
        products = Product.objects.prefetch_related('product_types').filter(available=True, custom=False)
        slug = self.kwargs['slug'] if 'slug' in self.kwargs else None
        if slug:
            collection = get_object_or_404(Collection, slug=slug)
            products = products.filter(collection=collection)
        return products

    def get_context_data(self):
        context = super().get_context_data(**self.kwargs)
        stock_dict = self.check_product_stock(context.get('products'))
        context['notification'] = Notification.objects.all()
        context['product_stock'] = stock_dict
        if 'collection_name' in self.kwargs:
            context['collection'] = get_object_or_404(Collection, name=self.kwargs['collection_name'])
            context['collection_name'] = self.kwargs['collection_name']
        context['collections'] = Collection.objects.filter(available=True, custom=False).order_by('-created')
        context['types'] = ProductType.objects.select_related('product')
        context['custom'] = False
        return context


class CustomProductsView(ListView):
    try:
        collection = None
        model = Product
        paginate_by = 9
        template_name = 'shop/product/custom_list.html'
        context_object_name = 'custom_products'
        temp = Product.objects.prefetch_related('product_types').filter(available=True, custom=True)
        gift_card = GiftCard.objects.filter(available=True)
        card_gift_cart_product_form = CartAddGiftCardProductForm()
        extra_context = {
            'view': 'shop:custom_products_view'
        }
    except OperationalError:
        pass

    def get_queryset(self):
        products = Product.objects.prefetch_related('product_types').filter(available=True, custom=True)
        slug = self.kwargs['slug'] if 'slug' in self.kwargs else None
        if slug:
            collection = get_object_or_404(Collection, slug=slug)
            products = products.filter(collection=collection)
        return products

    def get_context_data(self):
        context = super().get_context_data(**self.kwargs)
        context['notification'] = Notification.objects.all()
        if 'collection_name' in self.kwargs:
            context['collection'] = get_object_or_404(Collection, name=self.kwargs['collection_name'])
            context['collection_name'] = self.kwargs['collection_name']
        context['collections'] = Collection.objects.filter(available=True, custom=True).order_by('-created')
        context['types'] = ProductType.objects.select_related('product')
        context['custom'] = True
        return context


def get_icon(request):
    image_data = open(os.path.join(settings.STATIC_ROOT, 'images', 'icon.png'), "rb").read()
    return HttpResponse(image_data, content_type="image/png")


@login_required()
def generate_stripe_product(request, id: str):
    pr = Product.objects.filter(id=id)[0]
    success = stripe_product_generator.generate_product(pr)
    status = 'success' if success else 'failure'
    return JsonResponse(data={'status': status})
