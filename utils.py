def map_conversion_to_factor(conversion):

    if conversion.reverse:
        return 1 / conversion.factor
    else:
        return conversion.factor
