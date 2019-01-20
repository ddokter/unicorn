from django.utils.translation import ugettext_lazy as _
from django.http import HttpResponseRedirect
from django.forms import inlineformset_factory
from .base import CreateView, UpdateView
from unicorn.models.conversion import Conversion
from unicorn.models.expression import SubConversion


class FormSetMixin:

    def formset_label(self):

        return _("Subconversions")

    @property
    def formset(self):

        factory = inlineformset_factory(Conversion, SubConversion, exclude=[])

        kwargs = {}

        if self.request.method == "POST":
            kwargs['data'] = self.request.POST

        if self.object:
            kwargs['instance'] = self.object

        return factory(**kwargs)

    def form_valid(self, form):

        self.object = form.save()

        _formset = self.formset

        if _formset.is_valid():
            _formset.save()

        return HttpResponseRedirect(self.get_success_url())


class ConversionCreateView(FormSetMixin, CreateView):

    model = Conversion


class ConversionUpdateView(FormSetMixin, UpdateView):

    model = Conversion
