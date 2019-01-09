from operator import mul
from functools import reduce
from statistics import mean, median
from django import forms
from django.views.generic import FormView
from unicorn.models.unit import Unit
from unicorn.models.material import Material


class ConvertForm(forms.Form):

    from_unit = forms.ModelChoiceField(queryset=Unit.objects.all())
    to_unit = forms.ModelChoiceField(queryset=Unit.objects.all())
    material = forms.ModelChoiceField(queryset=Material.objects.all())


class ConvertView(FormView):

    template_name = "convert.html"
    form_class = ConvertForm
    paths = None

    def get(self, request, *args, **kwargs):

        self.form = self.get_form(self.form_class)

        return self.render_to_response(self.get_context_data(form=self.form))

    def post(self, request, *args, **kwargs):

        self.form = self.get_form(self.form_class)

        if self.form.is_valid():

            self.paths = self.form.cleaned_data['from_unit']. \
                find_conversion_paths(
                    self.form.cleaned_data['to_unit'],
                    self.form.cleaned_data['material'])

            return self.render_to_response(self.get_context_data(
                form=self.form, paths=self.paths))
        else:
            return self.form_invalid(self.form)

    def conversion_result(self):

        results = []
        precision = []

        def map_conversion_to_factor(conversion):

            factor = conversion.resolve(self.form.cleaned_data['to_unit'],
                                        self.form.cleaned_data['material'])

            if conversion.reverse:
                return 1 / factor
            else:
                return factor

        def map_conversion_to_precision(conversion):

            return conversion.get_precision()

        for path in self.paths:

            result = reduce(mul, map(map_conversion_to_factor, path), 1)
            _precision = reduce(mul, map(map_conversion_to_precision, path), 1)

            precision.append(_precision)
            results.append(result)

        return {
            'all': results,
            'precision': precision,
            'min': min(results),
            'max': max(results),
            'avg': mean(results),
            'median': median(results)
        }
