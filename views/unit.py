from statistics import mean, median
from django import forms
from django.views.generic import FormView
from django.views.generic.detail import SingleObjectMixin
from unicorn.models.unit import AbstractUnit, BaseUnit
from unicorn.models.material import Material
from .base import CTypeMixin


class ConvertForm(forms.Form):

    to_unit = forms.ModelChoiceField(queryset=BaseUnit.objects.all())
    material = forms.ModelChoiceField(queryset=Material.objects.all())


class UnitConvertView(FormView, SingleObjectMixin, CTypeMixin):

    template_name = "unit_convert.html"
    form_class = ConvertForm
    result = None
    model = AbstractUnit

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

        results = [path.factor for path in paths]

        if len(results):
            return {
                'paths': paths,
                'min': min(results),
                'max': max(results),
                'avg': mean(results),
                'median': median(results)
            }
        else:
            return None
