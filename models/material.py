from django.db import models
from django.utils.translation import ugettext_lazy as _


class Material(models.Model):

    name = models.CharField(_("Name"), max_length=100)

    def __str__(self):

        return self.name

    def list_conversions(self):

        return self.conversion_set.all()

    class Meta:
        app_label = "unicorn"
        ordering = ["name"]
