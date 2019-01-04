from django.db import models
from django.utils.translation import ugettext_lazy as _
from polymorphic.models import PolymorphicModel


class Material(PolymorphicModelma):

    name = models.CharField(_("Name"), max_length=100)

    def __str__(self):

        # return "%s %s" % (self._meta.verbose_name, self.name)
        return self.name

    class Meta:
        app_label = "unicorn"
        ordering = ["name"]
