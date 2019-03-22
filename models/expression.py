import operator as _op
from django.db import models
from django.utils.translation import ugettext_lazy as _
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

    def resolve(self, unit, material, exclude_id, year=None):

        """ Resolve, or thrown an exception """

        if unit == self.unit:

            return 1

        paths = self.unit.find_conversion_paths(
            unit, material,
            exclude_ids=[exclude_id],
            year=year)

        try:
            return paths[0].factor * self.amount
        except IndexError:
            raise UnresolvableExpression

    class Meta:

        app_label = "unicorn"
