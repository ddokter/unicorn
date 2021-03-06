from math import inf
from django.db import models
from django.db.models import Q
from django.apps import apps
from django.utils.translation import ugettext_lazy as _
from unicorn.path import Path, UnresolvableExpression
from .location import Location
from polymorphic.models import PolymorphicModel


# Do not seek any deeper than this... more conversions is probably a
# very unreliable path anyway.
#
MAX_DEPTH = 10

# Set the minimum precision needed as percentage/100 of the best
# result found. Only paths with a precision better than this are kept.
#
MIN_PRECISION = 0.8

# Set maximum path length as a factor of the shortest path found. Any
# paths longer than this will be discarded.
#
MAX_PATH_LENGTH = 2


QUANTITY = (
    (1, _("Mass")),
    (2, _("Volume")),
    (3, _("Mixed")),
)


STANDARD_SIZE_HELP = _("""Specify whether this size was a calibrated standard
size""")


STATUS = (
    (0, _("")),
    (1, _("Metric")),
    (2, _("Standard"))
)


class AbstractUnit(PolymorphicModel):

    """Base class for unit models, so as to be able to define both
    generic and local units, and let the Conversion model accept
    both.
    """

    name = models.CharField(_("Name"), null=True, blank=True, max_length=100)
    synonyms = models.CharField(_("Synonyms"), max_length=255,
                                null=True, blank=True)
    status = models.SmallIntegerField(_("Status"), default=0, choices=STATUS)
    quantity = models.SmallIntegerField(_("Quantity"), default=2,
                                        choices=QUANTITY)

    def find_conversion_paths(self, unit, material, _filter=None, year=None,
                              stack=None):

        """Find all possible conversion paths from self to the given unit. The
        returned list will be sorted on path length, shortest path
        first.

        """

        return sorted(
            list(self._find_conversion_paths(
                unit, material, _filter=_filter, year=year, _stack=stack)),
            key=lambda x: x.precision,
            reverse=True)

    def _find_conversion_paths(self, unit, material, _filter=None, year=None,
                               _stack=None):

        """Use breath-first to find the shortest paths for the conversion
        asked. The search will only be performed up to MAX_DEPTH, to
        prevent long searches for non existing conversions. Whenever a
        path is found, only paths where precision and length are
        within the boundaries set by MIN_PRECISION and MAX_PATH_LENGTH
        are considered.
        """

        conv_model = apps.get_model("unicorn", "Conversion")

        if _stack:
            path = Path(self, unit, material)
            for conv in _stack:
                path.append(conv)
            stack = [(_stack[0].to_unit, path)]
        else:
            stack = [(self, Path(self, unit, material))]

        # If last conversion on path is already what we are looking
        # for, yield this! Also, return since it looks like we're not
        # interested in more results...
        #
        if (_stack and (_stack[0].to_unit == unit or
                        _stack[0].from_unit == unit)):

            yield stack[0][1]
            return

        # Set shortest to infinity
        #
        shortest = inf

        # Set initial precision, so as to be able to cut off whenever the
        # precision is getting too low
        #
        precision = 0

        # Keep track of end points of the paths under scrutiny. Any
        # new end-point that is less precise than this, is discarded.
        #
        seen = {}

        while stack:

            (last_unit, path) = stack.pop(0)

            # Whenever the paths are getting too long, call it a day.
            #
            if (len(path) + 1 > shortest * MAX_PATH_LENGTH):
                break

            # Throw out paths that lack precision
            #
            if path.precision < precision * MIN_PRECISION:
                continue

            # stop whenever MAX_DEPTH is reached
            #
            if len(path) > MAX_DEPTH:
                break

            qs = conv_model.objects.exclude(id__in=[conv.id for conv in path])

            qs = qs.filter(source__enabled=True)

            qs = qs.exclude(status__lt=0)

            # Either the from and to units are both volume units and
            # the material is 'strict' (like barley)
            # or
            # the material is the same as the conversion or is in the
            # material categories
            #
            qs = qs.filter(
                Q(generic=True) |
                Q(
                    Q(from_unit__quantity=2) &
                    Q(to_unit__quantity=2) &
                    Q(material__strict_measurement=True)
                ) |
                Q(
                    Q(material=material) |
                    Q(material__in=material.categories.all())
                )
            )

            if year:
                qs = qs.filter(Q(year_to__gte=year) |
                               Q(year_to__isnull=True))

                qs = qs.filter(Q(year_from__lte=year) |
                               Q(year_from__isnull=True))

            qs = qs.find_for_unit(last_unit).distinct()

            if _filter:
                qs = qs.filter(**_filter)

            qs = qs.prefetch_related("to_unit", "from_unit")

            for conv in qs:

                try:
                    # We have a terminal conversion!
                    #
                    if conv.to_unit == unit or conv.from_unit == unit:

                        new_path = path.copy()
                        new_path.append(conv)

                        shortest = min(len(new_path), shortest)

                        precision = max(precision, new_path.precision)

                        yield new_path

                    else:
                        new_path = path.copy()
                        new_path.append(conv)

                        if conv.to_unit == last_unit:
                            end_unit = conv.from_unit
                        else:
                            end_unit = conv.to_unit

                        # If we have already seen this end unit in a path,
                        # with greater precision, we might as well throw
                        # the other ones away...
                        #
                        if (seen.get(end_unit.id, -inf) > new_path.precision):
                            continue
                        else:
                            seen[end_unit.id] = new_path.precision

                        # Discard conversions over different quantities
                        #
                        # if(conv.from_unit.quantity != conv.to_unit.quantity):
                        #    continue

                        stack.append((end_unit, new_path))

                except UnresolvableExpression:

                    # forget about this conversion...

                    pass

    def list_conversions(self):

        """ List conversions for this unit in both directions """

        _all = self.conversion_set.all()
        _rev = self.conversion_set_reverse.all()

        _all = _all.prefetch_related(*_all.model._prefetch_related)
        _rev = _rev.prefetch_related(*_rev.model._prefetch_related)

        _all.query.clear_ordering(True)
        _rev.query.clear_ordering(True)

        return _all.union(_rev)

    class Meta:

        app_label = "unicorn"
        ordering = ["name"]
        verbose_name_plural = _("Units")


class BaseUnit(AbstractUnit):

    """Base unit, not bound to a specific location. Used to specify metric
    units that apply in general.

    """

    def __str__(self):

        return self.name

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

    readonly = ['quantity']

    def __str__(self):

        return self.name or "%s (%s)" % (self.unit.name, self.location)

    def save(self, *args, **kwargs):

        self.quantity = self.unit.quantity

        super(LocalUnit, self).save(*args, **kwargs)

    class Meta:

        app_label = "unicorn"
        ordering = ["unit__name", "location__name"]
        verbose_name_plural = _("Local units")
