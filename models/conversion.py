from django.db import models
from django.db.models import F
from django.utils.translation import ugettext_lazy as _
from .unit import Unit
from .source import Source
from .material import Material


MARKERS = (('<', '<'), ('=', '='), ('>', '>'))


class ConversionQuerySet(models.QuerySet):

    def find_for_unit(self, unit):

        qs = super().filter(from_unit=unit).annotate(
            reverse=F('to_amount') - F('to_amount'))

        qs_reverse = super().filter(to_unit=unit).annotate(
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

    objects = ConversionManager()

    @property
    def ctype(self):

        return "conversion"

    def __str__(self):

        _str = "%.2f %s = %.2f %s" % (self.from_amount, self.from_unit,
                                      self.to_amount, self.to_unit)

        for sub in self.subconversion_set.all():

            _str = "%s %s" % (_str, sub)

        if self.material.exists():

            _str = "%s [%s]" % (
                _str,
                ", ".join([str(obj) for obj in self.material.all()]))

        return _str

    def resolve(self, unit, material):

        _res = self.to_amount / self.from_amount

        for sub in self.subconversion_set.all():

            _res = sub.get_operator()(_res, sub.resolve(unit, material))

        return _res

    class Meta:

        app_label = "unicorn"
        # ordering = ["from_unit__name"]
