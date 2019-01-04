from django.utils.translation import ugettext_lazy as _
from django.http import HttpResponseRedirect
from django.forms import inlineformset_factory
from .base import CreateView, UpdateView
from unicorn.models.recipe import Recipe


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
