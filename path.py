class Path(list):

    """Extend list to add some extra info, like the current conversion
    factor and the precision of the path found.
    """

    def __init__(self, from_unit, to_unit, material):

        self.factor = 1
        self.precision = 1
        self.from_unit = from_unit
        self.to_unit = to_unit
        self.material = material

        self._last_unit = from_unit

        return super().__init__()

    def __delitem__(self, idx):

        raise NotImplementedError

    def __mul__(self, value):

        raise NotImplementedError

    def append(self, conversion):

        self.precision *= conversion.get_precision()

        if self._last_unit == conversion.from_unit:
            self.factor *= conversion.resolve(self.material)
            self._last_unit = conversion.to_unit
        else:
            self.factor /= conversion.resolve(self.material)
            self._last_unit = conversion.from_unit

        return super().append(conversion)

    def clear(self):

        self.precision = 1
        self.factor = 1
        self._last_unit = self.from_unit

        return super().clear()

    def extend(self, path):

        assert(isinstance(path, self.__class__))

        self.precision *= path.precision
        self.factor *= path.factor
        self._last_unit = path._last_unit

        return super().extend(path)

    def _extend(self, path):

        return super().extend(path)

    def copy(self):

        new = Path(self.from_unit, self.to_unit, self.material)
        new._extend(self[:])

        new.precision = self.precision
        new.factor = self.factor
        new._last_unit = self._last_unit

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
