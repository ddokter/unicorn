import hashlib
from django.core.cache import cache as base_cache


def get_model_name(obj):

    return obj.__class__.__name__.lower()


def abbreviate(string, size):

    if len(string) < size:
        return string
    else:
        return "%s..." % string[:size]


def calculate_avg(paths):

    """ Path is supposed to be an array of Path objects """

    return (
        sum([path.factor * path.precision for path in paths]) /
        sum([path.precision for path in paths])
    )


def cache_get_key(*args, **kwargs):

    """ Generate cache key """

    def _get_key(obj):

        try:
            return obj.get_key()
        except:
            return str(obj)

    serialize = []
    for arg in args:
        serialize.append(_get_key(arg))

    for key, arg in kwargs.items():
        serialize.append(_get_key(key))
        serialize.append(_get_key(arg))

    key = hashlib.md5("".join(serialize).encode("utf-8")).hexdigest()

    return key


def cache(time=None):
    def decorator(fn):
        def wrapper(*args, **kwargs):
            key = cache_get_key(fn.__name__, *args, **kwargs)
            result = base_cache.get(key)
            if not result:
                result = fn(*args, **kwargs)
                base_cache.set(key, result, timeout=time)
            return result
        return wrapper
    return decorator


def obj_cache(time=None):

    def decorator(fn):
        def wrapper(*args, **kwargs):
            key = "%s-%s-%s" % (args[0]._meta.model.__name__,
                                args[0].id, fn.__name__)
            result = base_cache.get(key)
            if not result:
                result = fn(*args, **kwargs)
                base_cache.set(key, result, timeout=time)
            return result
        return wrapper
    return decorator
