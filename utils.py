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
