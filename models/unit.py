from django.db import models
from django.db.models import Q
from django.apps import apps
from django.utils.translation import ugettext_lazy as _
from unicorn.path import Path
from .location import Location
from polymorphic.models import PolymorphicModel


MAX_RELATIVE_PATH_LENGTH = 1.5
MAX_DEPTH = 10


class Unit(PolymorphicModel):

    """Any historic or modern unit. Location may be used to position the
    unit in a specific geographical place.
    """

    name = models.CharField(_("Name"), max_length=100)
    info = models.TextField(_("Description"), blank=True, null=True)

    def __str__(self):

        return self.name

    def find_conversion_paths(self, unit, material, date=None):

        """Find all possible conversion paths from self to the given unit. The
        returned list will be sorted on path length, shortest path
        first.

        """

        return sorted(
            list(self._find_conversion_paths(unit, material, date=date)),
            key=lambda x: x.precision,
            reverse=True)

    def _find_conversion_paths(self, unit, material, date=None):

        """Use breath-first to find the shortest paths for the conversion
        asked. The search will stop when no more paths exist that have a
        maximum length of 150% of the shortest path found.
        """

        conv_model = apps.get_model("unicorn", "Conversion")
        stack = [(self, Path(self, unit, material))]
        shortest_straw = -1

        # Set initial precision, so as to be able to cut off
        #
        precision = 0

        while stack:

            (last_unit, path) = stack.pop(0)

            # Whenever the paths are getting too long, call it a day.
            #
            if shortest_straw > -1 and len(path) > shortest_straw * 1.5:
                break

            # Throw out paths that lack precision
            #
            if path.precision < precision * 0.8:
                continue

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

            for conv in qs:

                # We have a terminal conversion!
                #
                if conv.to_unit == unit or conv.from_unit == unit:

                    path.append(conv)

                    if shortest_straw == -1:
                        shortest_straw = len(path)

                    precision = max(precision, path.precision)

                    yield path

                else:
                    new_path = path.copy()
                    new_path.append(conv)

                    if conv.to_unit == last_unit:
                        stack.append((conv.from_unit, new_path))
                    else:
                        stack.append((conv.to_unit, new_path))

    def list_conversions(self):

        """ List conversions for this unit in both directions """

        return self.conversion_set.all().union(
            self.conversion_set_reverse.all())

    class Meta:

        app_label = "unicorn"
        ordering = ["name"]


class LocalUnit(Unit):

    local_name = models.CharField(null=True, blank=True, max_length=100,
                                  unique=True)
    location = models.ForeignKey(Location, on_delete=models.CASCADE)

    def __str__(self):

        return self.local_name or "%s (%s)" % (self.name, self.location)
