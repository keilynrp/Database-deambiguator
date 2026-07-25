from enum import Enum


class StoreConnectionUpdatePlatformType0(str, Enum):
    BSALE = "bsale"
    CUSTOM = "custom"
    SHOPIFY = "shopify"
    WOOCOMMERCE = "woocommerce"

    def __str__(self) -> str:
        return str(self.value)
