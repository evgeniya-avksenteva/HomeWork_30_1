import stripe

from config.settings import API_KEY_STRIPE

stripe.api_key = API_KEY_STRIPE


# def create_stripe_product(name, description=""):
#     """Создает продукт в страйпе"""
#     product = stripe.Product.create(
#         name=name,
#         active=True,
#         description=description,
#     )
#     return product


def create_stripe_product(name, description=""):
    """Создает продукт в Stripe.description передаем
    только если она не пустая."""
    params = {
        "name": name,
        "active": True,
    }
    if description:
        params["description"] = description
    product = stripe.Product.create(**params)
    return product


def create_stripe_price(product_id, amount, currency="usd", recurring=None):
    """
    Создает цену для продукта в Stripe.
    amount — сумма в центах (например, 1000 = $10.00)
    recurring — словарь, например {"interval": "month"} для подписки, или None для разовой оплаты
    """
    params = {
        "currency": currency,
        "unit_amount": amount,
        "product": product_id,
    }
    if recurring:
        params["recurring"] = recurring
    price = stripe.Price.create(**params)
    return price


def create_stripe_checkout_session(price_id, quantity=1, success_url="", cancel_url=""):
    """Создает сессию оплаты и возвращает ссылку на оплату"""
    session = stripe.checkout.Session.create(
        success_url=success_url,
        cancel_url=cancel_url,
        line_items=[{"price": price_id, "quantity": quantity}],
        mode="payment",
    )
    return session
