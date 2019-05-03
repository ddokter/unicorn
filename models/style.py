from django.db import models
from django.utils.translation import ugettext_lazy as _


class Style(models.Model):

    """ Represent a given beer style, like Koyt, Kluyn, etc. """

    name = models.CharField(_("Name"), max_length=100)
    synonyms = models.CharField(_("Synonyms"), max_length=255,
                                null=True, blank=True)
    description = models.TextField(_("Description"), null=True, blank=True)

    def __str__(self):

        _str = self.name

        if self.synonyms:
            _str += " (%s)" % self.synonyms

        return _str

    def list_recipes(self):

        return self.recipe_set.all()

    class Meta:
        app_label = "unicorn"
        ordering = ["name"]
