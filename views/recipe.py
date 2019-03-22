from statistics import median
from django.utils.translation import ugettext_lazy as _
from django.http import HttpResponseRedirect
from django.forms import inlineformset_factory
from django import forms
from django.views.generic import FormView
from .base import CreateView, UpdateView
from django.views.generic.detail import SingleObjectMixin
from unicorn.models.recipe import Recipe
from unicorn.models.unit import BaseUnit
from unicorn.views.base import CTypeMixin


BREWHOUSE_EFF = 0.8

# Factor to compensate for the difference of modern day yield and the
# average yield of ye good old days.
#
YIELD_FACTOR = 0.75

# Extract, average, with compensation for old skool yield
#
EXTRACT = 0.8 * YIELD_FACTOR

# Rough estimate of Gravity Units added per kilo of material to a HL
# taking into account the lesser yield of old times
#
GU_PER_HL = 3 * YIELD_FACTOR

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
        queryset=BaseUnit.objects.all(),
        initial=BaseUnit.objects.filter(name='Liter').first()
    )
    material_to_unit = forms.ModelChoiceField(
        label=_("Material unit"),
        queryset=BaseUnit.objects.all(),
        initial=BaseUnit.objects.filter(name='Kilo').first())


class RecipeConvertView(FormView, SingleObjectMixin, CTypeMixin):

    template_name = "recipe_convert.html"
    model = Recipe
    form_class = ConvertForm
    converted_yield = None
    fermentables = None
    hops = None
    materials = {}

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super().post(request, *args, **kwargs)

    def form_valid(self, form):

        self.converted_yield = self._converted_yield(
            form.cleaned_data['yield_to_unit']
        )

        self.fermentables = self._converted_ingredients(
            form.cleaned_data['material_to_unit'],
            fermentable=True
        )

        self.hops = self._converted_ingredients(
            form.cleaned_data['material_to_unit'],
            fermentable=False
        )

        self.materials.update(self.fermentables)
        self.materials.update(self.hops)

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
            _yield += EXTRACT * BREWHOUSE_EFF * ingredient['amount']
            g_units += (GU_PER_HL * ingredient['amount'] * BREWHOUSE_EFF) / (
                self.converted_yield['amount'] / 100.0)

        density = (1000 + g_units) / 1000.0

        mass = self.converted_yield['amount'] * density

        plato = _yield / mass * 100

        og_units = (density - 1) * 1000

        total_weight = sum([ingr['amount'] for ingr in
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

        paths = self.object.amount_unit.find_conversion_paths(
            unit, None, year=self.object.year)

        if len(paths):

            _median = median([path.factor for path in paths])

            return {'amount': _median * self.object.amount,
                    'unit': unit,
                    'path': paths[0]}
        else:
            return {'amount': -1,
                    'unit': unit,
                    'path': []}

    def _converted_ingredients(self, unit, fermentable=True):

        results = {}

        for material in self.object.recipematerial_set.filter(
                material__fermentable=fermentable):

            paths = material.unit.find_conversion_paths(
                unit,
                material.material,
                year=self.object.year)

            if len(paths):

                _median = median([path.factor for path in paths])

                results[material.id] = {
                    'amount': _median * material.amount,
                    'unit': unit,
                    'path': paths[0]}
            else:
                results[material.id] = {
                    'amount': -1,
                    'unit': unit,
                    'path': []}

        return results
