import stripe
from django.conf import settings
from stripe.error import InvalidRequestError


class CouponCreator:
    def __init__(self):
        self.domain_url = settings.BASE_URL
        stripe.api_key = settings.STRIPE_SECRET_KEY
        self.delivery_products = settings.COUPON_EXCEPTIONS

    def create_coupon(self):
        # delete coupon
        try:
            stripe.Coupon.delete(
                sid=settings.COUPON_ID
            )
        except InvalidRequestError:
            print('delete error?')
            pass

        # get products
        products = [p.get('id') for p in stripe.Product.list(active=True).get('data') if
                    p.get('id') not in self.delivery_products]

        # create new coupon with list of products
        response = stripe.Coupon.create(
            percent_off=settings.COUPON_PERCENTAGE,
            duration="forever",
            name=settings.COUPON_ID,
            id=settings.COUPON_ID,
            applies_to=dict(products=products)
        )

        if response.get('valid'):
            return True
        return False
