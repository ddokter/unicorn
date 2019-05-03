from django.utils.translation import ugettext_lazy as _
from django.http import HttpResponseRedirect
from django.forms import inlineformset_factory
from django import forms
from django.views.generic import FormView
from .base import CreateView, UpdateView
from django.views.generic.detail import SingleObjectMixin
from unicorn.models.recipe import Recipe
from unicorn.models.unit import BaseUnit
from unicorn.models.material import Nonfermentable
from unicorn.views.base import CTypeMixin
from unicorn.utils import calculate_avg


BREWHOUSE_EFF = 0.8


# Hop utilization factor, assuming that all hops are boiled for a long
# time
#
HOP_UTILIZATION_FACTOR = 0.24

# Hop Alfa acid avg percentage
#
HOP_ALFA_ACID_PERC = 0.05


class FormSetMixin:

    def get_form(self, form_class=None):

        form = super().get_form(form_class=form_class)

        form.fields.pop('material')

        return form

    @property
    def formset_label(self):

        return _("Materials")

    @property
    def formset(self):

        factory = inlineformset_factory(Recipe, Recipe.material.through,
                                        exclude=[])

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


class RecipeCreateView(FormSetMixin, CreateView):

    model = Recipe


class RecipeUpdateView(FormSetMixin, UpdateView):

    model = Recipe


class ConvertForm(forms.Form):

    yield_to_unit = forms.ModelChoiceField(
        label=_("Yield unit"),
        queryset=BaseUnit.objects.all()
    )
    material_to_unit = forms.ModelChoiceField(
        label=_("Material unit"),
        queryset=BaseUnit.objects.all()
    )


class RecipeConvertView(FormView, SingleObjectMixin, CTypeMixin):

    template_name = "recipe_convert.html"
    model = Recipe
    form_class = ConvertForm
    converted_yield = None
    fermentables = None
    nonfermentables = None
    hops = None
    materials = {}
    units_found = {}

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super().post(request, *args, **kwargs)

    def get_form(self, form_class=None):

        form = super().get_form(form_class=form_class)

        form.fields['material_to_unit'].initial = BaseUnit.objects.filter(
            name='Kilo').first()

        form.fields['yield_to_unit'].initial = BaseUnit.objects.filter(
            name='Liter').first()

        return form

    def form_valid(self, form):

        self.converted_yield = self._converted_yield(
            form.cleaned_data['yield_to_unit']
        )

        self.fermentables = self._converted_fermentables(
            form.cleaned_data['material_to_unit']
        )

        self.hops = self._converted_hops(
            form.cleaned_data['material_to_unit']
        )

        self.nonfermentables = self._converted_nonfermentables(
            form.cleaned_data['material_to_unit']
        )

        self.materials.update(self.fermentables)
        self.materials.update(self.hops)
        self.materials.update(self.nonfermentables)

        return self.render_to_response(self.get_context_data(form=form))

    @property
    def gravity(self):

        """ Calculate degrees Plato if both yield and ingredients are
        found """

        if not (self.converted_yield and self.fermentables):
            return None

        if self.converted_yield['amount'] == -1:
            return None

        if min(map(lambda x: x['amount'],
                   self.fermentables.values())) < 0:
            return None

        # ok, we have it all...
        #
        _yield = 0
        g_units = 0

        for ingredient in self.fermentables.values():
            _yield += (ingredient['extract'] * BREWHOUSE_EFF *
                       ingredient['amount_malted'])

            g_units += (
                (ingredient['gu'] * ingredient['amount_malted'] *
                 BREWHOUSE_EFF) /
                (self.converted_yield['amount'] / 10))

        density = (1000 + g_units) / 1000.0

        mass = self.converted_yield['amount'] * density

        plato = _yield / mass * 100

        og_units = (density - 1) * 1000

        total_weight = sum([ingr['amount_malted'] for ingr in
                            self.fermentables.values()])

        return {'plato': plato,
                'og': density,
                'kghl': total_weight / (self.converted_yield['amount'] / 100),
                'alc': (og_units - og_units * 0.5) * 0.135}

    @property
    def ibu(self):

        if not (self.converted_yield and self.hops):
            return None

        if self.converted_yield['amount'] == -1:
            return None

        if min(map(lambda x: x['amount'],
                   self.hops.values())) < 0:
            return None

        if not self.gravity:
            return None

        _yield = 0

        # Compensate for OG if need be
        #
        _factor = max(1, (1 + ((self.gravity['og'] - 1.050) / 0.2)))

        for ingredient in self.hops.values():
            _yield += (HOP_UTILIZATION_FACTOR *
                       HOP_ALFA_ACID_PERC *
                       1000000 *
                       ingredient['amount'])

        return round(_yield / (self.converted_yield['amount'] * _factor))

    def _converted_yield(self, unit):

        beer = Nonfermentable.objects.filter(name='Bier').first()

        paths = self.object.amount_unit.find_conversion_paths(
            unit, beer, year=self.object.year)

        if len(paths):

            w_avg = calculate_avg(paths)

            return {'amount': w_avg * self.object.amount,
                    'unit': unit,
                    'wavg': w_avg,
                    'paths': paths}
        else:
            return {'amount': -1,
                    'unit': unit,
                    'wavg': -1,
                    'paths': []}

    def _converted_hops(self, unit):

        results = {}

        for material in self.object.list_hops():

            paths = self._get_paths(material, unit)

            if len(paths):

                w_avg = calculate_avg(paths)

                results[material.id] = {
                    'amount': w_avg * material.amount,
                    'unit': unit,
                    'wavg': w_avg,
                    'paths': paths}
            else:
                results[material.id] = {
                    'amount': -1,
                    'unit': unit,
                    'wavg': w_avg,
                    'paths': []}

        return results

    def _converted_nonfermentables(self, unit):

        results = {}

        for material in self.object.list_nonfermentables():

            paths = self._get_paths(material, unit)

            if len(paths):

                w_avg = calculate_avg(paths)

                results[material.id] = {
                    'amount': w_avg * material.amount,
                    'unit': unit,
                    'wavg': w_avg,
                    'paths': paths}
            else:
                results[material.id] = {
                    'amount': -1,
                    'unit': unit,
                    'wavg': w_avg,
                    'paths': []}

        return results

    def _converted_fermentables(self, unit):

        results = {}

        for material in self.object.list_fermentables():

            paths = self._get_paths(material, unit)

            if len(paths):

                w_avg = calculate_avg(paths)

                if material.malted:
                    # decrease with 22.5% due to calculations with actual
                    # grain
                    _factor = 0.775
                else:
                    # decrease weight for malting per hl, but volume
                    # increases by 7%
                    #
                    _factor = 1.07 * 0.775

                results[material.id] = {
                    'amount': w_avg * material.amount,
                    'amount_malted': w_avg * material.amount * _factor,
                    'extract': material.material.extract,
                    'gu': material.material.gu,
                    'unit': unit,
                    'wavg': w_avg,
                    'paths': paths}
            else:
                results[material.id] = {
                    'amount': -1,
                    'amount_malted': -1,
                    'extract': -1,
                    'gu': -1,
                    'unit': unit,
                    'wavg': -1,
                    'paths': []}

        return results

    def _get_paths(self, material, unit):

        if (material.unit, unit) in self.units_found:
            paths = self.units_found[(material.unit, unit)]
        else:
            paths = material.unit.find_conversion_paths(
                unit,
                material.material,
                year=self.object.year)

            self.units_found[(material.unit, unit)] = paths

        return paths
