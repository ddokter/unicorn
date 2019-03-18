def get_model_name(obj):

    return obj.__class__.__name__.lower()


def abbreviate(string, size):

    if len(string) < size:
        return string
    else:
        return "%s..." % string[:size]
