class PricingCatalog:
    """
    Cost Intelligence V1.

    Stores material and sheet pricing data.
    This is the future source of real supplier prices.
    """

    def __init__(
        self,
        prices=None,
    ):
        self.prices = prices or {}

    def get(
        self,
        stock_key,
    ):
        return self.prices.get(
            stock_key,
        )

    def set_price(
        self,
        stock_key,
        data,
    ):
        self.prices[stock_key] = data

    def has_price(
        self,
        stock_key,
    ):
        return stock_key in self.prices

    def list_stock_keys(
        self,
    ):
        return list(self.prices)

    def remove_price(
        self,
        stock_key,
    ):
        del self.prices[stock_key]
