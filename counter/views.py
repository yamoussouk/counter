from django.contrib.auth.decorators import login_required
from django.http import JsonResponse

from shop.CouponCreator import CouponCreator


@login_required()
def settings(request):
    cc = CouponCreator()
    response = cc.create_coupon()
    if response:
        return JsonResponse(data={'status': 'success'})
    return JsonResponse(data={'status': 'failure'})
