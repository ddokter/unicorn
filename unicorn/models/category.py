from django.db import models
from django.utils.translation import ugettext_lazy as _


class Category(models.Model):

    """Category for materials, so as to be able to 'superclass' them."""

    name = models.CharField(_("Name"), max_length=100)
    synonyms = models.CharField(_("Synonyms"), max_length=255,
                                null=True, blank=True)

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
