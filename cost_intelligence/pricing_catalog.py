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
