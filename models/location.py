from django.db import models
from django.apps import apps
from django.utils.translation import ugettext_lazy as _


class Location(models.Model):

    """ Any geographic location, be it a city or a village """

    name = models.CharField(_("Name"), max_length=100, unique=True)
    synonyms = models.CharField(_("Synonyms"), max_length=255,
                                null=True, blank=True)

    def __str__(self):

        return self.name

    def list_units(self):

        return self.localunit_set.all()

    def list_conversions(self):

        """ List all conversions for units within the same location """

        conv_model = apps.get_model("unicorn", "Conversion")
        local_unit_ids = [unit.id for unit in self.list_units()]

        return conv_model.objects.filter(to_unit__in=local_unit_ids).filter(
            from_unit__in=local_unit_ids)

    @property
    def child_fk_qs(self):

        localunit_model = apps.get_model("unicorn", "LocalUnit")

        return {
            'conversion': {
                'to_unit': localunit_model.objects.filter(location=self),
                'from_unit': localunit_model.objects.filter(location=self)
            },
            'localunit': {
                'location': Location.objects.filter(id=self.id)
            }
        }

    class Meta:

        app_label = "unicorn"
        ordering = ["name"]
