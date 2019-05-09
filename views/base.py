from django.views.generic.detail import DetailView as BaseDetailView
from django.views.generic.edit import CreateView as BaseCreateView
from django.views.generic.edit import UpdateView as BaseUpdateView
from django.views.generic.edit import DeleteView as BaseDeleteView
from django.views.generic import FormView
from django import forms
from django.urls import reverse, reverse_lazy
from django.urls.exceptions import NoReverseMatch
from django.utils.translation import ugettext_lazy as _
from django.apps import apps
from unicorn.utils import get_model_name


class SearchForm(forms.Form):

    query = forms.CharField(required=False)


class CTypeMixin(object):

    def get_model(self):

        if getattr(self, 'object', None):
            if hasattr(self.object, 'get_real_instance'):
                model = self.object.get_real_instance()._meta.model
            else:
                model = self.object._meta.model
        else:
            model = self.model

        return model

    @property
    def ctype(self):

        """ Determine content type, keeping in mind that some views are on
        polymorphic types
        """

        return self.get_model().__name__.lower()

    @property
    def ct_label(self):

        return _(self.get_model()._meta.verbose_name.capitalize())

    @property
    def view_type(self):

        """ Return one of: list, detail, edit, create, delete, other """

        return ""

    @property
    def view_name(self):

        """  Return a tuple of model name and view type """

        return (self.ctype, self.view_type)

    @property
    def listing_label(self):

        return _(self.get_model()._meta.verbose_name_plural.capitalize())

    @property
    def listing_url(self):

        return reverse_lazy("list", kwargs={'model': self.ctype})


class GenericMixin:

    _model = None

    @property
    def model(self):

        if self.kwargs.get('model', None):
            return apps.get_model("unicorn", self.kwargs['model'])
        else:
            return self._model

    @model.setter
    def model(self, value):

        self._model = value

    @property
    def success_url(self):

        modelname = self.kwargs.get('model', self.model.__name__.lower())

        return reverse("list", kwargs={'model': modelname})

    @property
    def cancel_url(self):

        return self.success_url


class InlineActionMixin:

    @property
    def parent(self):

        parent_model = apps.get_model("unicorn", self.kwargs['parent_model'])

        return parent_model.objects.get(id=self.kwargs['parent_pk'])

    def get_initial(self):

        return {self.fk_field: self.parent}

    @property
    def fk_field(self):

        return self.request.GET.get('fk_field', self.kwargs['parent_model'])

    @property
    def success_url(self):

        return reverse("view", kwargs={
            'pk': self.parent.pk,
            'model': self.kwargs['parent_model']
        })

    def get_form(self, form_class=None):

        form = super().get_form(form_class=form_class)

        try:
            field_defs = self.parent.child_fk_qs.get(self.ctype)

            for field in field_defs.keys():
                form.fields[field].queryset = field_defs[field]

        except:
            pass

        return form


class CreateView(GenericMixin, BaseCreateView, CTypeMixin):

    """ Base create view that enables creation within a parent """

    fields = "__all__"
    view_type = "create"

    def check_permission(self, request):

        permission = self.get_permission(request)

        if not permission:
            return True

        try:
            obj = self.get_object()
        except:
            try:
                obj = self.get_parent()
            except:
                obj = None

        return request.user.has_perm(permission, obj=obj)

    @property
    def permission(self):

        return "unicorn.add_%s" % self.ctype

    def get_template_names(self):

        return ["%s_create.html" % self.ctype, "base_create.html"]

    @property
    def action_url(self):

        try:
            action_url = reverse("%s_%s" % (self.view_type, self.ctype))
        except NoReverseMatch:
            action_url = reverse(self.view_type, kwargs={'model': self.ctype})

        return action_url


class UpdateView(GenericMixin, BaseUpdateView, CTypeMixin):

    fields = "__all__"
    view_type = "edit"

    @property
    def permission(self):

        return "unicorn.change_%s" % self.ctype

    def get_template_names(self):

        return ["%s_update.html" % self.ctype, "base_update.html"]

    @property
    def action_url(self):

        try:
            action_url = reverse("%s_%s" % (self.view_type, self.ctype),
                                 kwargs={'pk': self.object.id})
        except NoReverseMatch:
            action_url = reverse(self.view_type,
                                 kwargs={'model': self.ctype,
                                         'pk': self.object.id})

        return action_url


class DetailView(GenericMixin, BaseDetailView, CTypeMixin):

    view_type = "detail"

    @property
    def permission(self):

        return "unicorn.view_%s" % self.ctype

    def get_template_names(self):

        if self.template_name:
            return [self.template_name]

        return ["%s_detail.html" % self.ctype, "base_detail.html"]

    def properties(self):

        _props = []

        for field in self.object._meta.fields:
            _props.append((field.verbose_name,
                           getattr(self.object, field.attname)))

        return _props


class DeleteView(BaseDeleteView):

    """Delete view that takes a model as argument, and may take a
    list_url_name to point to the listing view of the specifiek model.

    """

    _model = None
    template_name = "confirm_delete.html"
    _list_url = None
    view_type = "delete"

    @property
    def model(self):

        if self.kwargs.get('model', None):
            return apps.get_model("unicorn", self.kwargs['model'])
        else:
            return self._model

    @model.setter
    def model(self, value):

        self._model = value

    @property
    def success_url(self):

        return reverse_lazy("list",
                            kwargs={'model': self.model.__name__.lower()})

    @success_url.setter
    def success_url(self, value):

        self._list_url = value

    @property
    def cancel_url(self):

        return self.success_url


class ListingView(GenericMixin, FormView, CTypeMixin):

    permission = "unicorn.manage_products"
    template_name = "base_listing.html"
    form_class = SearchForm
    query = None
    view_type = "list"

    def list_items(self):

        items = self.model.objects.all()

        if getattr(self.model, "_related", None):
            items = items.prefetch_related(*self.model._related)

        if self.query:

            items = [item for item in items if
                     self.query.lower() in str(item).lower()]

        return items

    def form_valid(self, form):

        self.query = form.cleaned_data['query']

        context = self.get_context_data()

        return self.render_to_response(context)


class InlineCreateView(InlineActionMixin, CreateView):

    @property
    def success_url(self):

        return reverse("view", kwargs={
            'pk': self.parent.pk,
            'model': get_model_name(self.parent)})

    @property
    def action_url(self):

        return reverse("inline_create", kwargs={
            'parent_pk': self.parent.id,
            'parent_model': get_model_name(self.parent),
            'model': self.ctype
        })


class InlineUpdateView(InlineActionMixin, UpdateView):

    @property
    def success_url(self):

        return reverse("view", kwargs={
            'pk': self.parent.pk,
            'model': get_model_name(self.parent)})

    @property
    def action_url(self):

        return reverse("inline_edit", kwargs={
            'parent_pk': self.parent.id,
            'parent_model': get_model_name(self.parent),
            'model': self.ctype,
            'pk': self.kwargs['pk']
        })


class InlineDeleteView(InlineActionMixin, DeleteView):

    pass
