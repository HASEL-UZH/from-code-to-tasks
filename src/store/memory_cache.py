class MemoryCache:
    store = {}

    def get_value(self, key: str, provider):
        value = self.store.get(key)
        if value is None:
            value = provider()
            self.store[key] = value

        return value
