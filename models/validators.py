from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


def is_range_01(value):

    """ Is it in the range 0..1? """

    if value < 0 or value > 1:
        raise ValidationError(
            _('%(value)s must be in the range [0..1]'),
            params={'value': value},
        )
