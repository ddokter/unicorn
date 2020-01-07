class UnresolvableExpression(Exception):

    """ When an expression cannot be resolved """


class Path(list):

    """Extend list to add some extra info, like the current conversion
    factor and the precision of the path found.
    """

    def __init__(self, from_node, to_node, material):

        self.precision = 1
        self.from_node = from_node
        self.to_node = to_node
        self.material = material
        self._last_node = from_node

        return super().__init__()

    @property
    def factor(self):

        _factor = 1
        _last_node = self.from_node

        for conv in self:
            if _last_node == conv.from_unit:
                _factor *= conv.resolve(self.material)
                _last_node = conv.to_unit
            else:
                _factor /= conv.resolve(self.material)
                _last_node = conv.from_unit

        return _factor

    def __delitem__(self, idx):

        raise NotImplementedError

    def __mul__(self, value):

        raise NotImplementedError

    def append(self, conversion):

        self.precision *= conversion.get_precision()

        if self._last_node == conversion.from_unit:
            self._last_node = conversion.to_unit
        else:
            self._last_node = conversion.from_unit

        return super().append(conversion)

    def clear(self):

        self.precision = 1
        self._last_node = self.from_node

        return super().clear()

    def extend(self, path):

        assert(isinstance(path, self.__class__))

        self.precision *= path.precision
        self._last_node = path._last_node

        return super().extend(path)

    def _extend(self, path):

        return super().extend(path)

    def copy(self):

        new = Path(self.from_node, self.to_node, self.material)
        new._extend(self[:])

        new.precision = self.precision
        new._last_node = self._last_node

        return new

    def insert(self, idx, conversion):

        raise NotImplementedError

    def pop(self, *args):

        raise NotImplementedError

    def remove(self, conversion):

        raise NotImplementedError

    def __add__(self, path):

        raise NotImplementedError

    __iadd__ = __add__
