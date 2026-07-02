import os


def _normalize_seed(value):
    if value is None:
        return None
    if isinstance(value, str):
        value = value.strip()
        if not value:
            return None
        try:
            return int(value, 0)
        except ValueError:
            return value
    return int(value)


# Set this to an integer or short string to make new runs generate the same world.
# Example values: 12345, 0xC0FFEE, "alpha-run"
DEFAULT_WORLD_SEED = _normalize_seed(os.getenv("SHADOWCASTER_WORLD_SEED"))
