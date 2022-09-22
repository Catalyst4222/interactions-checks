from weakref import WeakKeyDictionary


class Attribute:
    __slots__ = ("_mapping",)

    def __init__(self):
        self._mapping = WeakKeyDictionary()

    def __get__(self, instance, owner):
        try:
            return self._mapping[instance] if instance else self
        except KeyError:
            raise AttributeError from None

    def __set__(self, instance, value):
        self._mapping[instance] = value

    def __delete__(self, instance):
        del self._mapping[instance]
