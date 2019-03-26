from django.db import models
from django.utils.translation import ugettext_lazy as _
from .unit import AbstractUnit
from .material import Material
from .source import Source
from .style import Style
from .location import Location


class Recipe(models.Model):

    style = models.ForeignKey(Style, on_delete=models.CASCADE,
                              verbose_name=_("Style"))
    location = models.ForeignKey(Location, on_delete=models.CASCADE,
                                 verbose_name=_("Location"))
    date = models.DateField(_("Date"), null=True, blank=True)
    year = models.SmallIntegerField(_("Year of publication"))
    material = models.ManyToManyField(Material, through="RecipeMaterial")
    source = models.ForeignKey(Source, on_delete=models.CASCADE,
                               verbose_name=_("Source"))
    info = models.TextField(_("Information"), blank=True, null=True)
    amount = models.FloatField(_("Yield amount"))
    amount_unit = models.ForeignKey(AbstractUnit, on_delete=models.CASCADE,
                                    verbose_name=("Yield unit"))
    malt = models.BooleanField(_("Based on malted ingredients"), default=False)

    def __str__(self):

        return "%s (%s), A.D. %s" % (self.style.name, self.location, self.year)

    def list_fermentables(self):

        return [item for item in self.recipematerial_set.all()
                if item.material.__class__.__name__ == 'Fermentable']

    def list_hops(self):

        return [item for item in self.recipematerial_set.all()
                if item.material.__class__.__name__ == 'Hop']

    class Meta:
        ordering = ["style__name", "date"]
        app_label = "unicorn"
        verbose_name = _("Recipe")
        verbose_name_plural = _("Recipes")


class RecipeMaterial(models.Model):

    amount = models.FloatField(_("Amount"))
    unit = models.ForeignKey(AbstractUnit, on_delete=models.CASCADE)
    recepy = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    material = models.ForeignKey(Material, on_delete=models.CASCADE)
