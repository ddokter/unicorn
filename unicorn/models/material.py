from django.db import models
from django.utils.translation import ugettext_lazy as _
from polymorphic.models import PolymorphicModel
from beerlab.fermentable import FermentableMixin


STRICT_MEASUREMENT_HELP = """Defines whether this material was strictly
measured on markets, as opposed to materials that were measured in a lax
way to compensate for low weight/volume ratio."""


class Material(PolymorphicModel):

    name = models.CharField(_("Name"), max_length=100)
    strict_measurement = models.BooleanField(
        _("Strictly measured"),
        help_text=_(STRICT_MEASUREMENT_HELP),
        default=False)
    synonyms = models.CharField(_("Synonyms"), max_length=255,
                                null=True, blank=True)

    def __str__(self):

        return self.name

    def list_conversions(self):

        return self.conversion_set.all()

    class Meta:
        app_label = "unicorn"
        ordering = ["name"]


class Category(Material):

    """Category for materials, so as to be able to 'superclass' them."""

    def __str__(self):

        return self.name

    @property
    def byline(self):

        return self.synonyms

    def list_materials(self):

        return self.material_set.all()

    class Meta:
        app_label = "unicorn"
        ordering = ["name"]
        verbose_name_plural = _("Categories")


class MaterialBase(Material):

    categories = models.ManyToManyField('Category', blank=True)

    class Meta:
        abstract = True


class Fermentable(FermentableMixin, MaterialBase):

    """ Fermentable stuff, like malt. """

    extract = models.FloatField(_("Potential extract"), default=0.8)

    def get_extract(self):

        return self.extract

    class Meta:
        app_label = "unicorn"
        ordering = ["name"]
        verbose_name_plural = _("Fermentables")


class Hop(MaterialBase):

    """ Well... hop """

    alfa_acid = models.FloatField(_("Alfa acid"), default=5.0)

    class Meta:
        app_label = "unicorn"
        ordering = ["name"]
        verbose_name_plural = _("Hop")


class Nonfermentable(MaterialBase):

    """ Anything not hoppy, and not fermentable """

    class Meta:
        app_label = "unicorn"
        ordering = ["name"]
        verbose_name_plural = _("Nonfermentables")
