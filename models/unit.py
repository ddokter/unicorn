from math import inf
from django.db import models
from django.db.models import Q
from django.apps import apps
from django.utils.translation import ugettext_lazy as _
from unicorn.path import Path
from .location import Location
from polymorphic.models import PolymorphicModel


# Do not seek any deeper than this... more than 10 conversions is
# probably a very unreliable path anyway.
#
MAX_DEPTH = 10

# Set the minimum precision needed as percentage/100 of the best
# result found. Only paths with a precision better than this are kept.
#
MIN_PRECISION = 0.8

# Set maximum path length as a factor of the shortest path found. Any
# paths longer than this will be discarded.
#
MAX_PATH_LENGTH = 1.5


class AbstractUnit(PolymorphicModel):

    """Base class for unit models, so as to be able to define both
    generic and local units, and let the Conversion model accept
    both.
    """

    name = models.CharField(_("Name"), null=True, blank=True, max_length=100)
    synonyms = models.CharField(_("Synonyms"), max_length=255,
                                null=True, blank=True)

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
        asked. The search will only be performed up to MAX_DEPTH, to
        prevent long searches for non existing conversions. Whenever a
        path is found, only paths where precision and length are
        within the boundaries set by MIN_PRECISION and MAX_PATH_LENGTH
        are considered.

        """

        conv_model = apps.get_model("unicorn", "Conversion")
        stack = [(self, Path(self, unit, material))]
        shortest = inf

        # Set initial precision, so as to be able to cut off whenever the
        # precision is getting too low
        #
        precision = 0

        while stack:

            (last_unit, path) = stack.pop(0)

            # Whenever the paths are getting too long, call it a day.
            #
            if (len(path) > shortest * MAX_PATH_LENGTH):
                break

            # Throw out paths that lack precision
            #
            if path.precision < precision * MIN_PRECISION:
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

                    shortest = min(len(path), shortest)

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
        verbose_name_plural = _("Units")


class BaseUnit(AbstractUnit):

    """Base unit, not bound to a specific location. Used to specify metric
    units that apply to many places, and as a base for local units.

    """

    def __str__(self):

        _str = self.name

        if self.synonyms:
            _str += " (%s)" % self.synonyms

        return _str

    class Meta:

        app_label = "unicorn"
        ordering = ["name"]
        verbose_name_plural = _("Units")


class LocalUnit(AbstractUnit):

    """ Local unit, bound to a specific location """

    unit = models.ForeignKey(BaseUnit, on_delete=models.CASCADE,
                             verbose_name=_("Base unit"))
    location = models.ForeignKey(Location, on_delete=models.CASCADE,
                                 verbose_name=_("Location"))

    def __str__(self):

        return self.name or "%s (%s)" % (self.unit.name, self.location)

    class Meta:

        app_label = "unicorn"
        ordering = ["name"]
        verbose_name_plural = _("Local units")
