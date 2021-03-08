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
        all_products = []
        products = stripe.Product.list(active=True, limit=100)
        all_products.extend([p.get('id') for p in products.get('data') if p.get('id') not in self.delivery_products])
        while products.get('has_more'):
            products = stripe.Product.list(active=True, limit=100, starting_after=products.get('data')[-1])
            all_products.extend([p.get('id') for p in products.get('data') if p.get('id')
                                 not in self.delivery_products])

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
