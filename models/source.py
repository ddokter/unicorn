from django.db import models
from django.utils.translation import ugettext_lazy as _


def abbreviate(string, size):

    if len(string) < size:
        return string
    else:
        return "%s..." % string[:size]


class Source(models.Model):

    """ Represent historic sources of information """

    year = models.SmallIntegerField(_("Year of publication"))
    title = models.CharField(_("Title"), max_length=255)
    author = models.CharField(_("Author"), max_length=255)
    publisher = models.CharField(_("Publisher"), max_length=255,
                                 null=True, blank=True)
    other = models.TextField(_("Other info"), null=True, blank=True)
    original = models.BooleanField(_("Original source"), default=False)

    def __str__(self):

        return "%s, %s, %s" % (abbreviate(self.title, 50), self.author,
                               self.year)

    def list_conversions(self):

        return self.conversion_set.all().order_by("from_unit__name")

    class Meta:
        app_label = "unicorn"
        ordering = ["title"]
