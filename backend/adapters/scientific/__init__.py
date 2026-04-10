_REGISTRY: dict = {}


def register(name: str, cls):
    _REGISTRY[name] = cls


def get_scientific_adapter(source: str, config: dict = None):
    if source not in _REGISTRY:
        raise ValueError(
            f"Unknown scientific source: '{source}'. Available: {list(_REGISTRY)}"
        )
    return _REGISTRY[source](config or {})


def list_sources() -> list:
    return [
        {"id": k, "name": v.DISPLAY_NAME, "requires_key": v.REQUIRES_API_KEY}
        for k, v in _REGISTRY.items()
    ]
