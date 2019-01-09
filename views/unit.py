from operator import mul
from functools import reduce
from statistics import mean, median
from django import forms
from django.views.generic import FormView
from django.views.generic.detail import SingleObjectMixin
from unicorn.models.unit import Unit
from unicorn.models.material import Material


class ConvertForm(forms.Form):

    to_unit = forms.ModelChoiceField(queryset=Unit.objects.all())
    material = forms.ModelChoiceField(queryset=Material.objects.all())


class UnitConvertView(FormView, SingleObjectMixin):

    template_name = "unit_convert.html"
    form_class = ConvertForm
    result = None
    model = Unit

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super().post(request, *args, **kwargs)

    def form_valid(self, form):

        paths = self.object.find_conversion_paths(
            form.cleaned_data['to_unit'],
            form.cleaned_data['material'])

        self.result = self._result(paths,
                                   form.cleaned_data['to_unit'],
                                   form.cleaned_data['material'])

        return self.render_to_response(self.get_context_data(form=form))

    def _result(self, paths, to_unit, material):

        results = []
        precision = []

        def map_conversion_to_factor(conversion):

            factor = conversion.resolve(to_unit, material)

            if conversion.reverse:
                return 1 / factor
            else:
                return factor

        def map_conversion_to_precision(conversion):

            return conversion.get_precision()

        for path in paths:

            result = reduce(mul, map(map_conversion_to_factor, path), 1)
            _precision = reduce(mul, map(map_conversion_to_precision, path), 1)

            precision.append(_precision)
            results.append(result)

        return {
            'paths': paths,
            'all': results,
            'precision': precision,
            'min': min(results),
            'max': max(results),
            'avg': mean(results),
            'median': median(results)
        }
