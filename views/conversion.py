from django.utils.translation import ugettext_lazy as _
from django.http import HttpResponseRedirect
from django.forms import inlineformset_factory
from .base import CreateView, UpdateView, InlineCreateView, InlineUpdateView
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


class UnitOrderMixin(object):

    def get_form(self, form_class=None):

        form = super().get_form(form_class=form_class)

        qs = form.fields['to_unit'].queryset

        if qs.model.__name__ == "LocalUnit":
            qs = qs.order_by("unit", "location")
        else:
            qs = qs.order_by("localunit", "baseunit")

        form.fields['from_unit'].queryset = qs
        form.fields['to_unit'].queryset = qs

        return form


class ConversionCreateView(FormSetMixin, UnitOrderMixin, CreateView):

    model = Conversion


class ConversionUpdateView(FormSetMixin, UnitOrderMixin, UpdateView):

    model = Conversion


class InlineConversionCreateView(FormSetMixin, UnitOrderMixin,
                                 InlineCreateView):

    model = Conversion


class InlineConversionUpdateView(FormSetMixin, UnitOrderMixin,
                                 InlineUpdateView):

    model = Conversion
