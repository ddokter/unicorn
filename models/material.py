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

    class Meta:
        app_label = "unicorn"
        ordering = ["name"]
        verbose_name_plural = _("Fermentables")


class Hop(MaterialBase):

    """ Well... hop """

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
