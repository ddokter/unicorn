from django.template import Library
from django.urls import reverse
from unicorn.utils import get_model_name


register = Library()


@register.filter
def ctname(obj):

    return get_model_name(obj)


@register.inclusion_tag('snippets/listing.html', takes_context=True)
def listing(context, title, items, create_url=None):

    """ Show object listing """

    context.update({'title': title,
                    'items': items,
                    'create_url': create_url})

    return context


@register.inclusion_tag('snippets/sublisting.html', takes_context=True)
def sublisting(context, title, items, submodel, create_url=None):

    """ Show listing of items within object """

    context.update({'title': title,
                    'items': items,
                    'submodel': submodel,
                    'create_url': create_url})

    return context


@register.inclusion_tag('snippets/edit_action.html')
def edit_action(obj, btn_class=""):

    return {'edit_url': reverse("edit", kwargs={'model': get_model_name(obj),
                                                'pk': obj.id}),
            'btn_class': btn_class}


@register.inclusion_tag('snippets/edit_action.html')
def inline_edit_action(obj, parent, btn_class="", extra_args=""):

    return {'edit_url': "%s%s" % (reverse("inline_edit", kwargs={
        'parent_pk': parent.id,
        'parent_model': get_model_name(parent),
        'pk': obj.id,
        'model': get_model_name(obj)}), extra_args),
        'btn_class': btn_class}


@register.inclusion_tag('snippets/add_action.html')
def add_action(model, btn_class="", btn_label="Add"):

    model_name = model.__class__.__name__.lower()

    return {'create_url': reverse("create", kwargs={'model': model_name}),
            'btn_label': btn_label,
            'btn_class': btn_class}


@register.inclusion_tag('snippets/add_action.html')
def inline_add_action(model_name, parent, btn_class="", extra_args="",
                      btn_label="Add"):

    return {'create_url': "%s%s" % (reverse("inline_create", kwargs={
        'parent_pk': parent.id,
        'parent_model': get_model_name(parent),
        'model': model_name}), extra_args),
        'btn_class': btn_class,
        'btn_label': btn_label
    }


@register.inclusion_tag('snippets/delete_action.html')
def delete_action(obj, btn_class="", extra_args=""):

    return {'delete_url': "%s%s" % (reverse("delete", kwargs={
        'model': get_model_name(obj),
        'pk': obj.id}), extra_args), 'btn_class': btn_class}


@register.inclusion_tag('snippets/delete_action.html')
def inline_delete_action(obj, parent, btn_class="", extra_args=""):

    return {'delete_url': "%s%s" % (
        reverse("inline_delete", kwargs={
            'pk': obj.id,
            'model': get_model_name(obj),
            'parent_pk': parent.id,
            'parent_model': get_model_name(parent)}),
        extra_args), 'btn_class': btn_class}


@register.filter
def detail_url(obj):

    return reverse('view', kwargs={'model': get_model_name(obj), 'pk': obj.id})


@register.filter
def get(iterable, idx):

    return iterable[idx]
