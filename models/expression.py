import operator as _op
from functools import reduce
from django.db import models
from django.utils.translation import ugettext_lazy as _
from polymorphic.models import PolymorphicModel
from .unit import Unit
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
    unit = models.ForeignKey(Unit, on_delete=models.CASCADE)
    operator = models.CharField(_("Operator"),
                                max_length=1,
                                choices=OPERATORS)

    def __str__(self):

        _str = "%s %.2f %s" % (
            self.operator, self.amount, self.unit
        )

        return _str

    def get_operator(self):

        if self.operator == "-":
            return _op.sub
        else:
            return _op.add

    def resolve(self, unit, material):

        if unit == self.unit:

            return 1

        paths = self.unit.find_conversion_paths(unit, material)

        return paths[0].factor * self.amount

    class Meta:

        app_label = "unicorn"
        verbose_name = "expression"
        verbose_name_plural = "expressions"
