from django.db import models
from django.utils.translation import ugettext_lazy as _
from polymorphic.models import PolymorphicModel


class Material(PolymorphicModel):

    name = models.CharField(_("Name"), max_length=100)
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


class Fermentable(MaterialBase):

    """ Fermentable stuff, like malt. """

    extract = models.FloatField(_("Potential extract"), default=0.8)

    @property
    def gu(self):

        """ Calculate GU yield of 1 kg per 10 L (Based on PPG calculation) """

        gallon_conv_factor = 10 / 3.7854
        pound_conv_factor = 2.2046

        return (self.extract * 46 * pound_conv_factor) / gallon_conv_factor

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
