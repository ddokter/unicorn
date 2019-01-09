import operator as _op
from django.db import models
from django.db.models import F
from django.utils.translation import ugettext_lazy as _
from .unit import Unit
from .source import Source
from .material import Material


MARKERS = (('<', '<'), ('=', '='), ('>', '>'))
BASE_PRECISION = 0.98


class ConversionQuerySet(models.QuerySet):

    def find_for_unit(self, unit):

        """Find conversions for the given unit. This will find conversion
        that have the unit as 'to' value and 'from' value, but will
        exclude conversions that have complex 'to' values, using
        subconversions.
        """

        qs = super().filter(from_unit=unit).annotate(
            reverse=F('to_amount') - F('to_amount'))

        qs_reverse = super().filter(to_unit=unit).filter(
            subconversion__isnull=True).annotate(
            reverse=F('to_amount') - F('to_amount') + 1)

        return qs.union(qs_reverse)


class ConversionManager(models.Manager):

    def get_queryset(self):

        return ConversionQuerySet(self.model, using=self._db)


class Conversion(models.Model):

    from_amount = models.FloatField(_("From amount"), default=1.0)
    from_unit = models.ForeignKey(Unit, on_delete=models.CASCADE,
                                  related_name="conversion_set")
    to_amount = models.FloatField(_("To amount"), default=1.0)
    to_unit = models.ForeignKey(Unit, on_delete=models.CASCADE,
                                related_name="conversion_set_reverse")
    marker = models.CharField(_("Marker"), choices=MARKERS, max_length=1,
                              default="=")
    material = models.ManyToManyField(Material, blank=True)
    generic = models.BooleanField(_("Generic"), default=False)
    source = models.ManyToManyField(Source)
    year_from = models.SmallIntegerField(_("From year"), null=True, blank=True)
    year_to = models.SmallIntegerField(_("To year"), null=True, blank=True)
    original_text = models.TextField(_("Original text"), null=True, blank=True)
    precision = models.FloatField(blank=True, null=True)

    objects = ConversionManager()

    @property
    def ctype(self):

        return "conversion"

    def __str__(self):

        _str = "%.2f %s = %.2f %s" % (self.from_amount, self.from_unit,
                                      self.to_amount, self.to_unit)

        for sub in self.subconversion_set.all():

            _str = "%s %s" % (_str, sub)

        if self.material.exists() and False:

            _str = "%s [%s]" % (
                _str,
                ", ".join([str(obj) for obj in self.material.all()]))

        return _str

    def resolve(self, material):

        """ Resolve the conversion to it's 'to_unit'. If any subconversions
        are found, try to resolve these as well. """

        _res = self.to_amount / self.from_amount

        for sub in self.subconversion_set.all():

            _res = sub.get_operator()(_res,
                                      sub.resolve(self.to_unit, material))

        return _res

    def get_precision(self):

        """
        Calculate precision, in a range 0-1. This works as follows:
            1. if precision is specified on the model, return that
            2. if the conversion's from_unit location and to_unit location are
               the same, return BASE_PRECISION
            3. the bigger the difference in to_amount and from_amount, the less
               punishment
            4. more digits after the comma means more precision, hence, less
               punishment
        """

        _precision = BASE_PRECISION

        if self.precision:
            return self.precision
        elif self.to_unit.location == self.from_unit.location:
            return _precision

        rel = (min(self.from_amount, self.to_amount) /
               max(self.from_amount, self.to_amount))

        # Maximum of 10% punishment
        #
        _precision -= (rel * 0.05)

        # Maximum of 10% punishment
        #
        part = (len(str(self.from_amount).split('.')[1].strip('0')) +
                len(str(self.to_amount).split('.')[1].strip('0')))

        _precision -= ((1/pow(part + 1, 3)) * 0.05)

        return _precision

    class Meta:

        app_label = "unicorn"
        # ordering = ["from_unit__name"]
