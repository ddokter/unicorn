import operator as _op
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.db.models import F
from polymorphic.models import PolymorphicModel
from unicorn.path import UnresolvableExpression
from .unit import AbstractUnit
from .conversion import Conversion


OPERATORS = (
    ('+', '+'),
    ('-', '-'),
)


class Expression(PolymorphicModel):

    conversion = models.ForeignKey(Conversion, on_delete=models.CASCADE)

    class Meta:
        abstract = True


class SubConversion(Expression):

    amount = models.FloatField(_("Amount"))
    unit = models.ForeignKey(AbstractUnit, on_delete=models.CASCADE)
    operator = models.CharField(_("Operator"),
                                max_length=1,
                                choices=OPERATORS)

    def __str__(self):

        return "%s %.2f %s" % (self.operator, self.amount, self.unit)

    def get_operator(self):

        if self.operator == "-":
            return _op.sub
        else:
            return _op.add

    def resolve(self, unit, material, year=None):

        """ Resolve, or throw an exception. This resolve will only consider
        local conversions. """

        if unit == self.unit:

            return 1

        _filter = {
            'subconversion__isnull': True,
            'from_unit__localunit__location': F('to_unit__localunit__location')
        }

        paths = self.unit.find_conversion_paths(
            unit, material, year=year, _filter=_filter)

        try:
            return paths[0].result * self.amount
        except IndexError:
            raise UnresolvableExpression

    class Meta:

        app_label = "unicorn"
