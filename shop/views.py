from django.conf import settings
from django.db.utils import OperationalError
from django.http import HttpResponseRedirect
from django.shortcuts import redirect, reverse
from django.shortcuts import render, get_object_or_404
from django.views.generic.list import ListView

from cart.forms import CartAddProductForm, CartAddGiftCardProductForm
from shop.MessageSender import MessageSender
from .forms import ContactForm
from .models import Collection, Product, Notification, ProductType, GiftCard, Message


def index_hid(request):
    return render(request, 'shop/index.html')


def index(request):
    collections = Collection.objects.all()[:6]
    notification = Notification.objects.all()
    return render(request, 'shop/index_hid.html', {'collections': collections, 'notification': notification})


def product_list_by_collection(request, collection_name=None):
    collection = None
    collections = Collection.objects.all()
    products = Product.objects.filter(available=True)
    if collection_name:
        collection = get_object_or_404(Collection, name=collection_name)
        products = products.filter(collection=collection)
    notification = Notification.objects.all()
    return render(request, 'shop/product/list.html',
                  {'collection': collection, 'collections': collections, 'products': products,
                   'notification': notification})


def product_detail(request, id):
    product = get_object_or_404(Product, id=id, available=True)
    product_types = Product.objects.prefetch_related('product_types').filter(id=id, available=True)
    images = Product.objects.prefetch_related('images').filter(id=id, available=True)
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
    cart_product_form = CartAddProductForm()
    collections = Collection.objects.all()
    notification = Notification.objects.all()
    collection_name = product.collection.name
    return render(request, 'shop/product/detail.html',
                  {'product': product,
                   'notification': notification,
                   'collections': collections,
                   'collection_name': collection_name,
                   'types': types,
                   'cart_product_form': cart_product_form,
                   'is_stock': is_stock,
                   'images': imgs,
                   })


def faq(request):
    foxpost = settings.FOXPOST_PRICE
    delivery = settings.DELIVERY_PRICE
    csomagkuldo = settings.CSOMAGKULDO_PRICE
    notification = Notification.objects.all()
    return render(request, 'shop/faq.html',
                  {'csomagkuldo': csomagkuldo, 'foxpost': foxpost, 'delivery': delivery, 'notification': notification})


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
        temp = Product.objects.prefetch_related('product_types').filter(available=True)
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
            'card_gift_cart_product_form': card_gift_cart_product_form
        }
    except OperationalError:
        pass

    def check_product_stock(self, products) -> dict:
        stock_dict = dict()
        for p in products:
            pr = Product.objects.prefetch_related('product_types').filter(id=p.id, available=True)[0]
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
        products = Product.objects.prefetch_related('product_types').filter(available=True)
        collection_name = self.kwargs['collection_name'] if 'collection_name' in self.kwargs else None
        if collection_name:
            collection = get_object_or_404(Collection, name=collection_name)
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
        context['collections'] = Collection.objects.all()
        context['types'] = ProductType.objects.select_related('product')
        return context
