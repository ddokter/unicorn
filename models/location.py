from django.db import models
from django.apps import apps
from django.utils.translation import ugettext_lazy as _


class Location(models.Model):

    """ Any geographic location, be it a city or a village """

    name = models.CharField(_("Name"), max_length=100, unique=True)

    def __str__(self):

        return self.name

    def list_units(self):

        return self.unit_set.all()

    def list_conversions(self):

        """ List all conversions for units within the same location """

        conv_model = apps.get_model("unicorn", "Conversion")

        return conv_model.objects.filter(to_unit__location=self).filter(
            from_unit__location=self)

    class Meta:

        app_label = "unicorn"
        ordering = ["name"]
