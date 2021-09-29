from django.conf import settings
from django.shortcuts import redirect
from django.utils import timezone
from django.views.decorators.http import require_http_methods
from django.core.exceptions import ObjectDoesNotExist

from .forms import CouponApplyForm
from giftcardpayment.models import BoughtGiftCard
from .models import Coupon


def __get_amount(request):
    amount = 0
    discount = 0
    card_price = 0
    cart = request.session[settings.CART_SESSION_ID]
    for key, value in cart.items():
        if value.get('type') != 'gift_card':
            amount += int(value.get('price')) * value.get('quantity')
    if 'coupon_id' in request.session:
        try:
            discount = (Coupon.objects.get(id=request.session['coupon_id']).discount / 100) * amount
        except ObjectDoesNotExist:
            discount = 0
    if 'gift_card_ids' in request.session:
        temp = request.session['gift_card_ids']
        for t in temp:
            card_price += t["price"]
    amount = amount - discount - card_price
    return amount, discount


def _recalculate_coupon(request):
    return __get_amount(request)


@require_http_methods(['POST'])
def coupon_apply(request):
    now = timezone.now()
    form = CouponApplyForm(request.POST)
    if form.is_valid():
        code = form.cleaned_data['code']
        try:
            coupon = Coupon.objects.get(code__iexact=code,
                                        valid_from__lte=now,
                                        valid_to__gte=now,
                                        active=True)
            request.session['coupon_id'] = coupon.id
        except ObjectDoesNotExist:
            request.session['coupon_id'] = None
    request.session['current_amount'], request.session['current_coupon_amount'] = __get_amount(request)
    return redirect('cart:cart_detail')
