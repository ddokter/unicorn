from django.db.models import Q
from django.views.generic.detail import DetailView as BaseDetailView
from django.views.generic.edit import CreateView as BaseCreateView
from django.views.generic.edit import UpdateView as BaseUpdateView
from django.views.generic.edit import DeleteView as BaseDeleteView
from django.views.generic import FormView
from django import forms
from django.urls import reverse, reverse_lazy
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import ugettext_lazy as _


class SearchForm(forms.Form):

    query = forms.CharField(required=False)


class CTypeMixin(object):

    @property
    def ctype(self):

        return self.model.__name__.lower()

    @property
    def listing_label(self):

        return self.model._meta.verbose_name_plural.capitalize()

    @property
    def listing_url(self):

        return reverse_lazy(self.model._meta.verbose_name_plural)


class CreateView(BaseCreateView, CTypeMixin):

    """ Base create view that enables creation within a parent """

    list_url_name = ""
    fields = "__all__"

    @property
    def success_url(self):

        return reverse(self.model._meta.verbose_name_plural)

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

    @property
    def cancel_url(self):

        return self.success_url

    @property
    def action_url(self):

        return reverse("create_%s" % self.ctype)

    def get_template_names(self):

        return ["%s_create.html" % self.ctype, "base_create.html"]


class UpdateView(BaseUpdateView, CTypeMixin):

    fields = "__all__"

    @property
    def permission(self):

        return "unicorn.change_%s" % self.ctype

    @property
    def success_url(self):

        return reverse(self.model._meta.verbose_name_plural)

    @property
    def cancel_url(self):

        return reverse(self.model._meta.verbose_name_plural)

    @property
    def action_url(self):

        return reverse("edit_%s" % self.ctype, kwargs={'pk': self.object.pk})

    def get_template_names(self):

        return ["%s_update.html" % self.ctype, "base_update.html"]


class DetailView(BaseDetailView, CTypeMixin):

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

    model = None
    template_name = "confirm_delete.html"
    _list_url = None

    @property
    def success_url(self):

        return reverse_lazy(self.model._meta.verbose_name_plural)

    @success_url.setter
    def success_url(self, value):

        self._list_url = value

    @property
    def cancel_url(self):

        return reverse_lazy(self.model._meta.verbose_name_plural)


class ListingView(FormView, CTypeMixin):

    model = None
    permission = "unicorn.manage_products"
    template_name = "base_listing.html"
    form_class = SearchForm
    query = None

    def list_items(self):

        items = self.model.objects.all()

        if self.query:

            items = [item for item in items if
                     self.query.lower() in str(item).lower()]

        return items

    @property
    def model_label_plural(self):

        return _(self.model._meta.verbose_name_plural.capitalize())

    def get_detail_url(self, obj):

        return reverse('%s_detail' % obj._meta.vebose_name,
                       kwargs={'pk': obj.pk})

    def form_valid(self, form):

        self.query = form.cleaned_data['query']

        context = self.get_context_data()

        return self.render_to_response(context)


class InlineCreateView(CreateView):

    parent_model = None
    fk_field = None

    @property
    def parent(self):

        return self.parent_model.objects.get(id=self.kwargs['pk'])

    def get_initial(self):

        return {self.fk_field: self.parent}

    @property
    def success_url(self):

        return reverse("view_%s" % self.parent_model._meta.verbose_name,
                       kwargs={'pk': self.parent.pk})

    @property
    def action_url(self):

        return reverse("create_%s" % self.ctype, kwargs={'pk': self.parent.id})
