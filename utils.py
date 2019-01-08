from operator import mul
from functools import reduce
from statistics import mean, median


def conversion_result(paths, unit, material):

    results = []
    deviation = 0.99
    precision = []

    def map_conversion_to_factor(conversion):

        factor = conversion.resolve(unit, material)

        if conversion.reverse:
            return 1 / factor
        else:
            return factor

    for path in paths:

        result = reduce(mul, map(map_conversion_to_factor, path), 1)

        precision.append(pow(deviation, len(path)))
        results.append(result)

    return {
        'all': results,
        'precision': precision,
        'min': min(results),
        'max': max(results),
        'avg': mean(results),
        'median': median(results)
    }


def get_model_name(obj):

    return obj.__class__.__name__.lower()
