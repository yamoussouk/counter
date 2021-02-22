import stripe
from django.conf import settings
from stripe.error import InvalidRequestError


class StripeProductGenerator:
    def __init__(self):
        self.domain_url = settings.BASE_URL
        stripe.api_key = settings.STRIPE_SECRET_KEY

    def generate_product(self, product):
        product_name = product.name
        product_price = product.price
        product_price_api_id = product.price_api_id
        # if product_price_api_id
        prices = stripe.Price.list(limit=100, active=True)
        does_price_exist = product_price_api_id in [l.get('id') for l in prices.get('data')]
        if does_price_exist:
            return False
        else:
            # create a product
            created_product = stripe.Product.create(name=product_name)
            product_id = created_product.get('id')
            # create a price
            created_price = stripe.Price.create(
                unit_amount=int(product_price) * 100,
                currency="huf",
                product=product_id,
            )
            price_id = created_price.get('id')
        product.price_api_id = price_id
        product.save()
        return True
