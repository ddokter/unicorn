from django.utils.translation import ugettext_lazy as _
from django.http import HttpResponseRedirect
from django.forms import inlineformset_factory
from django import forms
from django.views.generic import FormView
from django.views.generic.detail import SingleObjectMixin
from .base import (CreateView, UpdateView, InlineCreateView, InlineUpdateView,
                   ListingView)
from unicorn.models.conversion import Conversion
from unicorn.models.expression import SubConversion
from statistics import mean
from unicorn.models.unit import AbstractUnit
from unicorn.models.material import Material
from unicorn.utils import calculate_avg
from .base import CTypeMixin


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


class OddConversions(ListingView):

    """ TODO: not used currently """

    model = Conversion

    def list_items(self):

        items = []

        for conv in self.model.objects.all():
            if (
                    self.model.objects.filter(from_unit=conv.from_unit).
                    filter(to_unit=conv.to_unit).exclude(id=conv.id).exists()
            ):
                items.append(conv)

        return items


class ConvertForm(forms.Form):

    to_unit = forms.ModelChoiceField(label=_("To unit"),
                                     queryset=AbstractUnit.objects.all())
    material = forms.ModelChoiceField(label=_("Material"),
                                      queryset=Material.objects.all())
    year = forms.IntegerField(label=_("Year"), required=False)


class ConversionConvertView(FormView, SingleObjectMixin, CTypeMixin):

    template_name = "conversion_convert.html"
    form_class = ConvertForm
    result = None
    model = Conversion

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super().post(request, *args, **kwargs)

    def form_valid(self, form):

        paths = self.object.from_unit.find_conversion_paths(
            form.cleaned_data['to_unit'],
            form.cleaned_data['material'],
            year=form.cleaned_data['year'],
            stack=[self.object]
        )

        self.result = self._result(paths,
                                   form.cleaned_data['to_unit'],
                                   form.cleaned_data['material'])

        return self.render_to_response(self.get_context_data(form=form))

    def _result(self, paths, to_unit, material):

        results = [path.factor for path in paths]

        if len(results):
            return {
                'paths': paths,
                'min': min(results),
                'max': max(results),
                'avg': mean(results),
                'w_avg': calculate_avg(paths)
            }
        else:
            return None
