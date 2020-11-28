from django.conf import settings
from django.shortcuts import redirect
from django.views.decorators.http import require_http_methods

from coupon.models import Coupon
from .forms import GiftCardApplyForm
from .models import BoughtGiftCard


def __get_amount(request):
    amount = 0
    discount = 0
    card_price = 0
    cart = request.session[settings.CART_SESSION_ID]
    for key, value in cart.items():
        amount += int(value.get('price')) * value.get('quantity')
    if 'coupon_id' in request.session:
        discount = (Coupon.objects.get(id=request.session['coupon_id']).discount / 100) * amount
    if 'gift_card_ids' in request.session:
        temp = request.session['gift_card_ids']
        for t in temp:
            card_price += BoughtGiftCard.objects.get(id=t).price
    amount = amount - discount - card_price
    return amount


@require_http_methods(['POST'])
def giftcard_apply(request):
    form = GiftCardApplyForm(request.POST)
    if form.is_valid():
        unique_uuid = form.cleaned_data['unique_uuid']
        try:
            card = BoughtGiftCard.objects.get(unique_uuid__iexact=unique_uuid, active=True)
            if 'gift_card_ids' in request.session:
                temp = request.session['gift_card_ids']
                if card.id not in temp:
                    temp.append(card.id)
                request.session['gift_card_ids'] = temp
            else:
                request.session['gift_card_ids'] = [card.id]
        except BoughtGiftCard.DoesNotExist:
            pass
    request.session['current_amount'] = __get_amount(request)
    return redirect('payment:process')
