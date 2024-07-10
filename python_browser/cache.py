import time


def now() -> int:
    return int(time.time())


def calc_cache_expiry(max_age: int) -> int:
    return now() + max_age


# Ex. 1-8
class BrowserCache:
    def __init__(self):
        self._cache = {}

    # Default max age = 0 seconds from now, i.e. no caching
    def add(self, key: str, value: str, max_age: int = 0):
        expiry_s = calc_cache_expiry(max_age)
        self._cache[key] = {"data": value, "expiry_s": expiry_s}

    def remove(self, key):
        if self._cache.get(key):
            del self._cache[key]

    def get(self, key: str) -> str | None:
        val = self._cache.get(key)
        if val is None:
            return None

        expiry = val.get("expiry_s")
        if expiry is not None and expiry <= now():
            self.remove(key)
            return None
        else:
            return val.get("data")

    def has(self, key: str) -> bool:
        return self.get(key) is not None

    def evict_expired(self):
        for key, val in self._cache.items():
            expiry = val.get("expiry_s")
            if expiry is not None and expiry <= now():
                self.remove(key)


browser_cache = BrowserCache()
