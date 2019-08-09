class CacheKeyMixin:

    def get_key(self):

        return "%s-%s" % (self._meta.model.__name__, self.id)
