from django.db import models
from django.db.models import Q
from django.apps import apps
from django.utils.translation import ugettext_lazy as _
from .location import Location


MAX_RELATIVE_PATH_LENGTH = 1.5
MAX_DEPTH = 10


class Unit(models.Model):

    """ Any historic or modern unit """

    name = models.CharField(_("Name"), max_length=100)
    location = models.ForeignKey(Location, blank=True, null=True,
                                 on_delete=models.CASCADE)

    def __str__(self):

        _str = self.name

        if self.location:

            _str = "%s (%s)" % (_str, self.location)

        return _str

    def find_conversion_paths(self, unit, material, date=None):

        """Find all possible conversion paths from self to the given unit. The
        returned list will be sorted on path length, shortest path
        first.

        """

        return list(self._find_conversion_paths(
            unit, material, date=date))

    def _find_conversion_paths(self, unit, material, date=None):

        """Use breath-first to find the shortest paths for the conversion
        asked. The search will stop when no more paths exist that have a
        maximum length of 150% of the shortest path found.
        """

        conv_model = apps.get_model("unicorn", "Conversion")
        stack = [(self, [])]
        shortest_straw = -1

        while stack:

            (last_unit, path) = stack.pop(0)

            # Whenever the paths are getting too long, call it a day.
            #
            if shortest_straw > -1 and len(path) > shortest_straw * 1.5:
                break

            # stop whenever MAX_DEPTH is reached
            #
            if len(path) > MAX_DEPTH:
                break

            qs = conv_model.objects.exclude(
                id__in=[conv.id for conv in path])

            qs = qs.filter(Q(material=material) | Q(generic=True))

            if date:
                qs = qs.filter(Q(date_from__lte=date) |
                               Q(date_from__isnull=True)).filter(
                                   Q(date_to__gte=date) |
                                   Q(date_to__isnull=True))

            qs = qs.find_for_unit(last_unit)

            for next in qs:
                if next.to_unit == unit or next.from_unit == unit:
                    if shortest_straw == -1:
                        shortest_straw = len(path) + 1
                    yield path + [next]
                elif next.to_unit == last_unit:
                    stack.append((next.from_unit, path + [next]))
                else:
                    stack.append((next.to_unit, path + [next]))

    def list_conversions(self):

        """ List conversions for this unit in both directions """

        return self.conversion_set.all().union(
            self.conversion_set_reverse.all())

    class Meta:

        app_label = "unicorn"
        ordering = ["name"]
        unique_together = ("name", "location")
