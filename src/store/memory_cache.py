from typing import Any


class MemoryCache:
    def __init__(self):
        self._store = {}

    def get_value(self, key: str, provider):
        value = self._store.get(key)
        if value is None:
            value = provider()
            self._store[key] = value

        return value


class Memento:
    def __init__(self, provider):
        self._provider = provider
        self._value: Any = None
        self._set = False

    def value(self):
        if not self._set:
            self._value = self._provider()
            self._set = True
        return self._value
