import logging
import os
import re
import logging
from django.db.models import Q
from django.utils.text import slugify

from django.db.models import Case, When
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.db.utils import OperationalError
from django.http import HttpResponse
import json
from django.http import HttpResponseRedirect
from django.http import JsonResponse
from django.shortcuts import redirect, reverse
from django.shortcuts import render, get_object_or_404
from django.views.decorators.http import require_http_methods
from django.views.generic.list import ListView

from cart.forms import CartAddProductForm, CartAddCustomProductForm, CartAddGiftCardProductForm
from parameters.models import Parameter
from shop.MessageSender import MessageSender
from .StripeProductGenerator import StripeProductGenerator
from .forms import ContactForm
from .models import Collection, Product, Notification, ProductType, GiftCard, Message
from django_user_agents.utils import get_user_agent

stripe_product_generator = StripeProductGenerator()
log = logging.getLogger(__name__)


def mobile(request):
    MOBILE_AGENT_RE = re.compile(r".*(iphone|mobile|androidtouch)", re.IGNORECASE)
    if MOBILE_AGENT_RE.match(request.META['HTTP_USER_AGENT']):
        return True
    else:
        return False


def index_hid(request):
    return render(request, 'shop/index.html')


def index(request):
    coll = Collection.objects.filter(available=True, custom=False, show_on_home_page=True)
    basic_collection = [c for c in coll if c.basic_collection and not c.best_seller_collection]
    temp = [c for c in coll if c.regular_collection and not c.best_seller_collection]
    regular_collections = sorted(temp, key=lambda x: x.created, reverse=True)[:3]
    temp = [c for c in coll if not c.basic_collection and not c.regular_collection and not c.best_seller_collection]
    temporary_collections = sorted(temp, key=lambda x: x.created, reverse=True)[:9]
    temp = [c for c in coll if c.best_seller_collection]
    best_sellers_collection = sorted(temp, key=lambda x: x.created)
    # basic_collection = Collection.objects.filter(available=True, custom=False, show_on_home_page=True,
    #                                              basic_collection=True, best_seller_collection=False)
    if len(basic_collection):
        basic_products = Product.objects.filter(collection=basic_collection[0])
    else:
        basic_products = []
    # regular_collections = Collection.objects.filter(available=True, custom=False, show_on_home_page=True,
    #                                                 regular_collection=True, best_seller_collection=False).order_by('-created')[:3]
    # temporary_collections = (
    #     Collection.objects.filter(available=True, custom=False, show_on_home_page=True, basic_collection=False,
    #                               regular_collection=False, best_seller_collection=False)
    #         .order_by('-created')[:9])
    # best_sellers_collection = Collection.objects.filter(available=True, custom=False, show_on_home_page=True,
    #                                                     best_seller_collection=True).order_by('-created')
    if len(best_sellers_collection):
        bs_products = Product.objects.filter(collection=best_sellers_collection[0])
    else:
        bs_products = []
    notification = Notification.objects.all()
    is_mobile = mobile(request)
    param = Parameter.objects.filter(name="shipping_information")
    shipping_information = param[0].value if len(param) and param[0].active else None
    ratio = 0.93 if is_mobile else 2.44
    context = dict(basic_collection=basic_collection, basic_products=basic_products,
                   regular_collections=regular_collections, temporary_collections=temporary_collections,
                   notification=notification, ratio=ratio, shipping_information=shipping_information,
                   best_sellers_collection=best_sellers_collection, bs_products=bs_products, device=mobile(request))
    return render(request, 'shop/index_hid.html', context)


def __get_product_details(request, id: str, slug: str, custom: bool, studio: bool, referer: str):
    try:
        collection = Collection.objects.filter(slug=id)[0]
    except (Collection.DoesNotExist, IndexError):
        log.info(f'Exception in getting product details - Collection slug {id}')
        return render(request, 'shop/404_termek.html', {})
    try:
        product = Product.objects.filter(collection=collection, slug=slug, available=True, custom=custom)[0]
    except (Product.DoesNotExist, IndexError):
        log.info(f'Exception in getting product details - Product slug {slug}')
        return render(request, 'shop/404_termek.html', {})
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
    basic_collections = [] if studio else Collection.objects.filter(
        available=True, basic_collection=True, custom=custom, studio_collection=False).order_by('-created')
    regular_collections = [] if studio else Collection.objects.filter(available=True, custom=custom,
                                                                      regular_collection=True,
                                                                      studio_collection=False).order_by('-created')
    temporary_collections = [] if studio else Collection.objects.filter(available=True, custom=custom,
                                                                        basic_collection=False,
                                                                        regular_collection=False,
                                                                        best_seller_collection=False,
                                                                        studio_collection=False).order_by('-created')
    # find if there is utolsó darabok
    temp = list(temporary_collections)
    upper = [e.name for e in temp if e.name.isupper()]
    if len(upper):
        idx_of_upper = [idx for idx, u in enumerate(temp) if u.name == upper[0]][0]
        temp.append(temp.pop(idx_of_upper))
    notification = Notification.objects.all()
    collection_slug = '' if studio else product.collection.slug
    view = 'shop:studio_products_view' if studio else ('shop:custom_products_view' if custom else 'shop:products_view')
    template = 'shop/product/custom_detail.html' if custom else 'shop/product/detail.html'
    param = Parameter.objects.filter(name="shipping_information")
    nemes_acel = Parameter.objects.filter(name="nemesacel_beszuro")[0].value
    muanyag = Parameter.objects.filter(name="muanyag_beszuro")[0].value
    nikkel_mentes = Parameter.objects.filter(name="nikkel_mentes")[0].value
    shipping_information = param[0].value if len(param) and param[0].active else None
    if referer == settings.MAIN_URL or referer is None:
        if studio:
            referer = settings.MAIN_URL + 'slowstudio'
        else:
            referer = settings.MAIN_URL + 'termekek/' + product.collection.slug
    return render(request, template,
                  {'product': product,
                   'notification': notification,
                   'basic_collections': basic_collections,
                   'regular_collections': regular_collections,
                   'temporary_collections': temp,
                   'collection_slug': collection_slug,
                   'types': types,
                   'cart_product_form': cart_product_form,
                   'is_stock': is_stock,
                   'images': imgs,
                   'view': view,
                   'slug': collection_slug,
                   'shipping_information': shipping_information,
                   'nemes_acel': nemes_acel,
                   'muanyag': muanyag,
                   'nikkel_mentes': nikkel_mentes,
                   'referer': referer,
                   'device': mobile(request)
                   })


def product_detail(request, id: str, slug: str):
    referer = request.META.get('HTTP_REFERER')
    return __get_product_details(request, id, slug, False, False, referer)


def studio_product_detail(request, id: str, slug: str):
    referer = request.META.get('HTTP_REFERER')
    return __get_product_details(request, id, slug, False, True, referer)


def custom_product_detail(request, id: str, slug: str):
    referer = request.META.get('HTTP_REFERER')
    return __get_product_details(request, id, slug, True, False, referer)


def faq(request):
    foxpost = Parameter.objects.filter(name="foxpost_price")[0].value
    delivery = Parameter.objects.filter(name="delivery_price")[0].value
    csomagkuldo = Parameter.objects.filter(name="csomagkuldo_price")[0].value
    ajanlott = Parameter.objects.filter(name="ajanlott_price")[0].value
    notification = Notification.objects.all()
    param = Parameter.objects.filter(name="shipping_information")
    shipping_information = param[0].value if len(param) and param[0].active else None
    seo_title = "Gyakori kérdések"
    seo_description = "Gyakori kérdések - kényelmes megoldás Önnek, ha otthonról vásárolna."
    return render(request, 'shop/faq.html',
                  {'csomagkuldo': csomagkuldo, 'foxpost': foxpost, 'delivery': delivery,
                   'ajanlott': ajanlott, 'notification': notification, 'shipping_information': shipping_information,
                   'seo_title': seo_title,
                   'seo_description': seo_description,
                   'device': mobile(request)})


def contact(request):
    contact_form = ContactForm()
    notification = Notification.objects.all()
    param = Parameter.objects.filter(name="shipping_information")
    shipping_information = param[0].value if len(param) and param[0].active else None
    seo_title = "Kapcsolat"
    seo_description = "Kapcsolat - kényelmes megoldás Önnek, ha otthonról vásárolna."
    return render(request, 'shop/contact.html', {'contact_form': contact_form, 'notification': notification,
                                                 'shipping_information': shipping_information,
                                                 'seo_title': seo_title,
                                                 'seo_description': seo_description,
                                                 'device': mobile(request)})


def data_handling(request):
    notification = Notification.objects.all()
    param = Parameter.objects.filter(name="shipping_information")
    shipping_information = param[0].value if len(param) and param[0].active else None
    seo_title = "Adatkezelési tájékoztató"
    seo_description = "Adatkezelési tájékoztató - kényelmes megoldás Önnek, ha otthonról vásárolna."
    return render(request, 'shop/data_handling.html', {'notification': notification,
                                                       'shipping_information': shipping_information,
                                                       'seo_title': seo_title,
                                                       'seo_description': seo_description,
                                                       'device': mobile(request)})


def aszf(request):
    notification = Notification.objects.all()
    param = Parameter.objects.filter(name="shipping_information")
    shipping_information = param[0].value if len(param) and param[0].active else None
    seo_title = "Vásárlási feltételek"
    seo_description = "Vásárlási feltételek - kényelmes megoldás Önnek, ha otthonról vásárolna."
    return render(request, 'shop/aszf.html', {'notification': notification,
                                              'shipping_information': shipping_information,
                                              'seo_title': seo_title,
                                              'seo_description': seo_description,
                                              'device': mobile(request)})


def contact_message(request):
    form = ContactForm(request.POST)
    if form.is_valid():
        cd = form.cleaned_data
        subject = cd['subject']
        email = cd['email']
        message = cd['message']
        name = cd['name']
        result = MessageSender('Kapcsolat e-mail a minervastudio.hu oldalról', settings.EMAIL_HOST_USER, email,
                               f'Feladó:\n{name}\nFeladó Email címe: {email}\nTárgy:\n{subject}\nÜzenet:\n{message}').send_mail()
        sent = True if result == 1 else False
        Message.objects.create(subject=subject, email=email, message=message, name=name,
                               sender='System message from Minerva Studio', sent=sent)
        return redirect(reverse('shop:thank_you'))
    else:
        print('error', form.errors.as_data())
        contact_form = ContactForm()
    return render(request, 'shop/contact.html', {'contact_form': contact_form, 'device': mobile(request)})


def thank_you(request):
    return render(request, 'shop/thank_you.html')


def impresszum(request):
    notification = Notification.objects.all()
    param = Parameter.objects.filter(name="shipping_information")
    shipping_information = param[0].value if len(param) and param[0].active else None
    seo_title = "Impresszum"
    seo_description = "Impresszum - kényelmes megoldás Önnek, ha otthonról vásárolna."
    return render(request, 'shop/impresszum.html', {'notification': notification,
                                                    'shipping_information': shipping_information,
                                                    'seo_title': seo_title,
                                                    'seo_description': seo_description,
                                                    'device': mobile(request)})


def _get_stock_list(temp):
    stock_dict = dict()
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
    return stock_dict


class ProductsView(ListView):
    try:
        collection = None
        model = Product
        paginate_by = 9
        template_name = 'shop/product/list.html'
        context_object_name = 'products'
        temp = Product.objects.prefetch_related('product_types').filter(available=True, custom=False,
                                                                        collection__available=True,
                                                                        collection__studio_collection=False)
        stock_dict = _get_stock_list(temp)
        gift_card = GiftCard.objects.filter(available=True)
        card_gift_cart_product_form = CartAddGiftCardProductForm()
        param = Parameter.objects.filter(name="shipping_information")
        shipping_information = param[0].value if len(param) and param[0].active else None
        extra_context = {
            'product_stock': stock_dict,
            'gift_card': gift_card,
            'card_gift_cart_product_form': card_gift_cart_product_form,
            'view': 'shop:products_view',
            'product_view': 'shop:product_detail',
            'shipping_information': shipping_information
        }
    except OperationalError:
        pass

    def check_product_stock(self, products) -> dict:
        return _get_stock_list(products)

    def get_queryset(self):
        products = Product.objects.prefetch_related('product_types').filter(available=True, custom=False,
                                                                            collection__available=True,
                                                                            collection__studio_collection=False)
        self.kwargs["stock_dict"] = stock_dict = _get_stock_list(products)
        keys = [[k, stock_dict[k]] for k in list(stock_dict.keys())]
        sorted_list = sorted(keys, key=lambda x: not x[1])
        sorted_list = [sl[0] for sl in sorted_list]
        preserved = Case(*[When(pk=pk, then=pos) for pos, pk in enumerate(sorted_list)])
        products = Product.objects.prefetch_related('product_types').filter(pk__in=sorted_list).order_by(preserved)

        slug = self.kwargs['slug'] if 'slug' in self.kwargs else None
        if slug:
            collection = Collection.objects.filter(slug=slug)
            collection = collection[0] if len(collection) else None
            products = products.filter(collection=collection)
        return products

    def get_context_data(self):
        context = super().get_context_data(**self.kwargs)
        stock_dict = self.kwargs["stock_dict"]
        context['notification'] = Notification.objects.all()
        context['product_stock'] = stock_dict
        if 'collection_name' in self.kwargs:
            context['collection'] = get_object_or_404(Collection, name=self.kwargs['collection_name'])
            context['collection_name'] = self.kwargs['collection_name']
        if 'slug' in self.kwargs:
            context['collection'] = get_object_or_404(Collection, slug=self.kwargs['slug'])
        else:
            context['collection'] = dict(seo_title='Fülbevaló választék, kézműves fülbevalók - Minervastudio',
                                         seo_description='Egyedi, kézzel készített fülbevalók süthető gyurmából '
                                                         'és nemesacél elemekkel, csak Neked.')
        context['basic_collections'] = Collection.objects.filter(
            available=True, basic_collection=True, custom=False, studio_collection=False).order_by('-created')
        context['regular_collections'] = Collection.objects.filter(available=True, custom=False,
                                                                   regular_collection=True,
                                                                   studio_collection=False).order_by('-created')
        temporary_collections = Collection.objects.filter(available=True, custom=False,
                                                          basic_collection=False,
                                                          regular_collection=False,
                                                          studio_collection=False,
                                                          best_seller_collection=False).order_by('-created')
        # find if there is utolsó darabok
        temp = list(temporary_collections)
        upper = [e.name for e in temp if e.name.isupper()]
        if len(upper):
            idx_of_upper = [idx for idx, u in enumerate(temp) if u.name == upper[0]][0]
            temp.append(temp.pop(idx_of_upper))
        context['temporary_collections'] = temp
        context['types'] = ProductType.objects.select_related('product')
        context['custom'] = False
        context['device'] = mobile(self.request)
        return context


class SearchProductsView(ListView):
    try:
        model = Product
        paginate_by = 12
        template_name = 'shop/product/list.html'
        context_object_name = 'products'
        gift_card = GiftCard.objects.filter(available=True)
        card_gift_cart_product_form = CartAddGiftCardProductForm()
        param = Parameter.objects.filter(name="shipping_information")
        shipping_information = param[0].value if len(param) and param[0].active else None
        extra_context = {
            'gift_card': gift_card,
            'card_gift_cart_product_form': card_gift_cart_product_form,
            'view': 'shop:products_view',
            'product_view': 'shop:studio_product_detail'
        }
    except OperationalError:
        pass

    def get_queryset(self):
        products = Product.objects.prefetch_related('product_types').filter(available=True, custom=False,
                                                                            collection__studio_collection=False)
        self.kwargs["stock_dict"] = _get_stock_list(products)
        keys = [[k, self.kwargs["stock_dict"][k]] for k in list(self.kwargs["stock_dict"].keys())]
        sorted_list = sorted(keys, key=lambda x: not x[1])
        sorted_list = [sl[0] for sl in sorted_list]
        preserved = Case(*[When(pk=pk, then=pos) for pos, pk in enumerate(sorted_list)])
        products = Product.objects \
            .prefetch_related('product_types') \
            .filter(pk__in=sorted_list, available=True, custom=False, collection__studio_collection=False) \
            .order_by(preserved)
        tag = self.request.GET['kulcsszo']
        self.kwargs["keyword"] = tag
        products = [product for product in products if product.is_tag(tag)]

        return products

    def get_context_data(self):
        context = super().get_context_data(**self.kwargs)
        context['product_stock'] = self.kwargs["stock_dict"]
        context['keyword'] = self.kwargs["keyword"]
        context['notification'] = Notification.objects.all()
        context['collection'] = dict(seo_title='Fülbevaló választék, kézműves fülbevalók - Minervastudio',
                                     seo_description='Egyedi, kézzel készített fülbevalók süthető gyurmából '
                                                     'és nemesacél elemekkel, csak Neked.')
        context['basic_collections'] = Collection.objects.filter(
            available=True, basic_collection=True, custom=False, studio_collection=False).order_by('-created')
        context['regular_collections'] = Collection.objects.filter(available=True, custom=False,
                                                                   regular_collection=True,
                                                                   studio_collection=False).order_by('-created')
        temporary_collections = Collection.objects.filter(available=True, custom=False,
                                                          basic_collection=False,
                                                          regular_collection=False,
                                                          studio_collection=False,
                                                          best_seller_collection=False).order_by('-created')
        # find if there is utolsó darabok
        temp = list(temporary_collections)
        upper = [e.name for e in temp if e.name.isupper()]
        if len(upper):
            idx_of_upper = [idx for idx, u in enumerate(temp) if u.name == upper[0]][0]
            temp.append(temp.pop(idx_of_upper))
        context['temporary_collections'] = temp
        context['types'] = ProductType.objects.select_related('product')
        context['custom'] = False
        context['device'] = mobile(self.request)
        return context


class StudioProductsView(ListView):
    try:
        collection = None
        model = Product
        paginate_by = 24
        template_name = 'shop/product/list.html'
        context_object_name = 'products'
        stock_dict = dict()
        temp = Product.objects.prefetch_related('product_types').filter(available=True, custom=False,
                                                                        collection__available=True,
                                                                        collection__studio_collection=True)
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
            'view': 'shop:studio_products_view',
            'product_view': 'shop:studio_product_detail'
        }
    except OperationalError:
        pass

    def check_product_stock(self, products) -> dict:
        stock_dict = dict()
        for p in products:
            pr = Product.objects.prefetch_related('product_types').filter(id=p.id, available=True, custom=False,
                                                                          collection__available=True,
                                                                          collection__studio_collection=True
                                                                          )[0]
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
        products = Product.objects.prefetch_related('product_types').filter(available=True, custom=False,
                                                                            collection__available=True,
                                                                            collection__studio_collection=True)
        self.kwargs["stock_dict"] = stock_dict = _get_stock_list(products)
        keys = [[k, stock_dict[k]] for k in list(stock_dict.keys())]
        sorted_list = sorted(keys, key=lambda x: not x[1])
        sorted_list = [sl[0] for sl in sorted_list]
        preserved = Case(*[When(pk=pk, then=pos) for pos, pk in enumerate(sorted_list)])
        products = Product.objects.prefetch_related('product_types').filter(pk__in=sorted_list).order_by(preserved)

        slug = self.kwargs['slug'] if 'slug' in self.kwargs else None
        if slug:
            collection = Collection.objects.filter(slug=slug)
            collection = collection[0] if len(collection) else None
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
        context['basic_collections'] = []
        context['regular_collections'] = []
        temporary_collections = []
        # find if there is utolsó darabok
        temp = list(temporary_collections)
        upper = [e.name for e in temp if e.name.isupper()]
        if len(upper):
            idx_of_upper = [idx for idx, u in enumerate(temp) if u.name == upper[0]][0]
            temp.append(temp.pop(idx_of_upper))
        context['temporary_collections'] = temp
        context['types'] = ProductType.objects.select_related('product')
        context['custom'] = False
        context['device'] = mobile(self.request)
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
        context['basic_collections'] = Collection.objects.filter(
            available=True, basic_collection=True, custom=True).order_by('-created')
        context['regular_collections'] = Collection.objects.filter(available=True, custom=True,
                                                                   regular_collection=True).order_by('-created')
        temporary_collections = Collection.objects.filter(available=True, custom=True,
                                                          basic_collection=False,
                                                          regular_collection=False).order_by('-created')
        # find if there is utolsó darabok
        temp = list(temporary_collections)
        upper = [e.name for e in temp if e.name.isupper()]
        if len(upper):
            idx_of_upper = [idx for idx, u in enumerate(temp) if u.name == upper[0]][0]
            temp.append(temp.pop(idx_of_upper))
        context['temporary_collections'] = temp
        context['types'] = ProductType.objects.select_related('product')
        context['custom'] = True
        context['device'] = mobile(self.request)
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


def name_validation(request, name: str):
    slug = slugify(name)
    response_data = {"exist": Product.objects.filter(slug=slug).exists()}
    return HttpResponse(json.dumps(response_data), content_type="application/json")


def price_api_key(request, price: str):
    try:
        api_key = getattr(settings, f'PA_{price}')
    except AttributeError:
        api_key = f'No API Key found by {price}. Please create one in stripe and let me know!'
    response_data = {"api_key": api_key}
    return HttpResponse(json.dumps(response_data), content_type="application/json")

# def view_404(request, exception=None):
#     return redirect('/')
