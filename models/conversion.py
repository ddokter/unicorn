from django.db import models
from django.db.models import Q
from django.utils.translation import ugettext_lazy as _
from .source import Source
from .material import Material
from .unit import AbstractUnit
from .validators import is_range_01


MARKERS = (('<', '<'), ('=', '='), ('>', '>'))

STATUS = (
    (1, _("Reference")),
    (2, _("Inferred")),
    (3, _("Ambiguous")),
    (4, _("Asumption")),
    (5, _("Anomalous"))
)

# No conversion is considered to be more precise than this. Based on
# calculations done by Zevenboom.
#
BASE_PRECISION = 0.98

# if status is ambiguous, punish
#
AMBIGOUS_CONVERSION_PUNISHMENT = 0.8


class ConversionQuerySet(models.QuerySet):

    def find_for_unit(self, local_unit):

        """Find conversions for the given unit. This will find conversion
        that have the unit as 'to' value and 'from' value, but will
        exclude conversions that have complex 'to' values, using
        subconversions.
        """

        return super().filter(
            Q(from_unit=local_unit) |
            (Q(to_unit=local_unit) & Q(subconversion__isnull=True))
        )


class ConversionManager(models.Manager):

    def get_queryset(self):

        return ConversionQuerySet(self.model, using=self._db)


class Conversion(models.Model):

    from_amount = models.FloatField(_("From amount"), default=1.0)
    from_unit = models.ForeignKey(
        AbstractUnit, on_delete=models.CASCADE,
        related_name="conversion_set", verbose_name=_("From unit"))
    to_amount = models.FloatField(_("To amount"), default=1.0)
    to_unit = models.ForeignKey(
        AbstractUnit, on_delete=models.CASCADE,
        related_name="conversion_set_reverse", verbose_name=_("To unit"))
    marker = models.CharField(_("Marker"), choices=MARKERS, max_length=1,
                              default="=")
    material = models.ManyToManyField(Material, blank=True)
    generic = models.BooleanField(_("Generic"), default=False)
    source = models.ManyToManyField(Source)
    year_from = models.SmallIntegerField(_("From year"), null=True, blank=True)
    year_to = models.SmallIntegerField(_("To year"), null=True, blank=True)
    original_text = models.TextField(_("Original text"), null=True, blank=True)
    precision = models.FloatField(blank=True, null=True,
                                  validators=[is_range_01])
    status = models.SmallIntegerField(_("Status"), default=1, choices=STATUS)

    objects = ConversionManager()

    @property
    def ctype(self):

        return "conversion"

    def __str__(self):

        _str = "%.2f %s %s %.2f %s" % (
            self.from_amount, self.from_unit,
            self.marker, self.to_amount, self.to_unit)

        for sub in self.subconversion_set.all():

            _str = "%s %s" % (_str, sub)

        return _str

    def resolve(self, material, year=None):

        """ Resolve the conversion to it's 'to_unit'. If any subconversions
        are found, try to resolve these as well. """

        _res = self.to_amount / self.from_amount

        for sub in self.subconversion_set.all():

            _res = sub.get_operator()(
                _res,
                sub.resolve(self.to_unit, material, year=year))

        return _res

    def get_factor(self):

        return self.from_amount / self.to_amount

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
        elif (getattr(self.to_unit, 'location', None) ==
              getattr(self.from_unit, 'location', None)):
            return _precision

        rel = (min(self.from_amount, self.to_amount) /
               max(self.from_amount, self.to_amount))

        # Maximum of 5% punishment
        #
        _precision *= (1 - rel * 0.05)

        # Maximum of 5% punishment
        #
        part = (len(str(self.from_amount).split('.')[1].strip('0')) +
                len(str(self.to_amount).split('.')[1].strip('0')))

        _precision *= (1 - (1/pow(part + 1, 3)) * 0.05)

        # Punish non exact conversion
        if self.marker != '=':
            _precision *= BASE_PRECISION

        if self.status == 3:
            _precision *= AMBIGOUS_CONVERSION_PUNISHMENT

        return _precision

    class Meta:

        app_label = "unicorn"
        ordering = ["from_unit__name"]
