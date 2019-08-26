import re
from django.db import models
from django.utils.translation import ugettext_lazy as _
from unicorn.utils import abbreviate


class Source(models.Model):

    """Represent historic and not so historic sources of information"""

    title = models.CharField(_("Title"), max_length=255)
    year = models.SmallIntegerField(_("Year of publication"),
                                    null=True, blank=True)
    author = models.CharField(_("Author"), max_length=255,
                              null=True, blank=True)
    publisher = models.CharField(_("Publisher"), max_length=255,
                                 null=True, blank=True)
    description = models.TextField(_("Description"), null=True, blank=True)
    enabled = models.BooleanField(_("Enabled"), default=True)
    online_version = models.URLField(null=True, blank=True)

    def __str__(self):

        _str = [abbreviate(self.title, 50)]

        for attr in ['year', 'author', 'publisher']:

            if getattr(self, attr, None):
                _str.append(str(getattr(self, attr)))

        return ", ".join(_str)

    def list_conversions(self):

        return self.conversion_set.all().order_by("from_unit__name")

    @property
    def abbr(self):

        """ Abbreviate source """

        if self.author:
            _abbr = re.compile("[.\s]").split(self.author)[-1].lower()
        else:
            _abbr = self.title.split()[0].lower()

        if self.year:
            _abbr += " %s" % self.year

        return _abbr

    class Meta:
        app_label = "unicorn"
        ordering = ["title"]
