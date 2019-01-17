from django.db import models
from django.utils.translation import ugettext_lazy as _
from unicorn.models.unit import AbstractUnit
from unicorn.models.material import Material
from unicorn.models.source import Source
from unicorn.models.style import Style


class Recipe(models.Model):

    """Represent a beer recepy. The recipe must be specified by it's name
    (e.g. Koyt, Kluyn, etc.)"""

    style = models.ForeignKey(Style, on_delete=models.CASCADE,
                              verbose_name=_("Style"))
    date = models.DateField(_("Date"), null=True, blank=True)
    year = models.SmallIntegerField(_("Year of publication"))
    material = models.ManyToManyField(Material, through="RecipeMaterial")
    source = models.ForeignKey(Source, on_delete=models.CASCADE,
                               verbose_name=_("Source"))
    info = models.TextField(_("Information"), blank=True, null=True)
    amount = models.FloatField(_("Yield amount"))
    amount_unit = models.ForeignKey(AbstractUnit, on_delete=models.CASCADE,
                                    verbose_name=("Yield unit"))

    def __str__(self):

        return "%s %s" % (self.style.name, self.year)

    class Meta:
        ordering = ["style__name", "date"]
        app_label = "unicorn"


class RecipeMaterial(models.Model):

    amount = models.FloatField(_("Amount"))
    unit = models.ForeignKey(AbstractUnit, on_delete=models.CASCADE)
    recepy = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    material = models.ForeignKey(Material, on_delete=models.CASCADE)
