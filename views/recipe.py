from django.utils.translation import ugettext_lazy as _
from django.http import HttpResponseRedirect
from django.forms import inlineformset_factory
from .base import CreateView, UpdateView, DetailView
from unicorn.models.recipe import Recipe
from unicorn.models.unit import Unit
from unicorn.models.material import Material
from unicorn.utils import conversion_result


BREWHOUSE_EFF = 0.8

YIELD_FACTOR = 0.75


# Extract, average, with compensation for old skool yield
#
EXTRACT = 0.8 * YIELD_FACTOR

# Rough estimate of Gravity Units added per kilo of material to a HL
# taking into account the lesser yield of old times
#
GU_PER_HL = 3 * YIELD_FACTOR


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


class RecipeConvertView(DetailView):

    template_name = "recipe_convert.html"
    model = Recipe

    converted_yield = None
    converted_ingredients = None

    def render_to_response(self, context):

        self.calculate_values()

        return super().render_to_response(context)

    def calculate_values(self):

        self.converted_yield = self._converted_yield()
        self.converted_ingredients = self._converted_ingredients()

    @property
    def gravity(self):

        """ Calculate degrees Plato if both yield and ingredients are
        found """

        if not self.converted_yield and self.converted_ingredients:
            return None

        if self.converted_yield['amount'] == -1:
            return None

        if min(map(lambda x: x['amount'],
                   self.converted_ingredients.values())) < 0:
            return None

        # ok, we have it all...
        #
        _yield = 0
        g_units = 0

        for ingredient in self.converted_ingredients.values():
            _yield += EXTRACT * BREWHOUSE_EFF * ingredient['amount']
            g_units += (GU_PER_HL * ingredient['amount'] * BREWHOUSE_EFF) / (
                self.converted_yield['amount'] / 100.0)

        density = (1000 + g_units) / 1000.0

        mass = self.converted_yield['amount'] * density

        plato = _yield / mass * 100

        og_units = (density - 1) * 1000

        return {'plato': plato,
                'og': density,
                'alc': (og_units - og_units * 0.5) * 0.135}

    def _converted_yield(self):

        liter = Unit.objects.filter(name="Liter").first()
        beer = Material.objects.filter(name="Bier").first()

        paths = self.object.amount_unit.find_conversion_paths(liter, beer)

        if len(paths):

            res = conversion_result(paths, self.object.amount_unit, beer)

            return {'amount': res['median'] * self.object.amount,
                    'unit': liter,
                    'path': paths[0]}
        else:
            return {'amount': -1,
                    'unit': liter,
                    'path': []}

    def _converted_ingredients(self):

        kilo = Unit.objects.filter(name="Kilo").first()

        results = {}

        for material in self.object.recipematerial_set.all():

            paths = material.unit.find_conversion_paths(kilo,
                                                        material.material)

            if len(paths):

                res = conversion_result(paths, self.object.amount_unit,
                                        material.material)

                results[material.id] = {
                    'amount': res['median'] * material.amount,
                    'unit': kilo,
                    'path': paths[0]}
            else:
                results[material.id] = {
                    'amount': -1,
                    'unit': kilo,
                    'path': []}

        return results
