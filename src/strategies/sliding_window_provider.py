from typing import Any


class SlidingWindowProvider:
    def __init__(self, items: [Any], window_size):
        self._items = items
        self._window_size = window_size
        self._index = 0

    def __iter__(self):
        return self

    def __next__(self):
        if self._index + self._window_size > len(self._items):
            raise StopIteration

        window = self._items[self._index : self._index + self._window_size]
        self._index += 1
        return window
