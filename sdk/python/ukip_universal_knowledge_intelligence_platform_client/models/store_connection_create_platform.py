from enum import Enum


class StoreConnectionCreatePlatform(str, Enum):
    BSALE = "bsale"
    CUSTOM = "custom"
    SHOPIFY = "shopify"
    WOOCOMMERCE = "woocommerce"

    def __str__(self) -> str:
        return str(self.value)
