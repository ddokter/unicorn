from django.template import Library
from django.urls import reverse
from django.urls.exceptions import NoReverseMatch
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
def sublisting(context, title, items, submodel, fk_field=None):

    """ Show listing of items within object """

    context.update({'title': title,
                    'items': items,
                    'submodel': submodel})

    if fk_field:
        context.update({'extra_args': '?fk_field=%s' % fk_field})

    return context


@register.inclusion_tag('snippets/edit_action.html')
def edit_action(obj):

    model_name = get_model_name(obj)

    try:
        _url = reverse("edit_%s" % model_name, kwargs={'pk': obj.id})
    except NoReverseMatch:
        _url = reverse("edit", kwargs={'model': model_name, 'pk': obj.id})
    return {'edit_url': _url}


@register.inclusion_tag('snippets/edit_action.html')
def inline_edit_action(obj, parent, extra_args=""):

    return {'edit_url': "%s%s" % (reverse("inline_edit", kwargs={
        'parent_pk': parent.id,
        'parent_model': get_model_name(parent),
        'pk': obj.id,
        'model': get_model_name(obj)}), extra_args)}


@register.inclusion_tag('snippets/add_action.html')
def add_action(model):

    model_name = model.__class__.__name__.lower()

    try:
        create_url = reverse("create_%s" % model_name)
    except NoReverseMatch:
        create_url = reverse("create", kwargs={'model': model_name})
    return {'create_url': create_url}


@register.inclusion_tag('snippets/add_action.html')
def inline_add_action(model_name, parent, extra_args=""):

    return {'create_url': "%s%s" % (reverse("inline_create", kwargs={
        'parent_pk': parent.id,
        'parent_model': get_model_name(parent),
        'model': model_name}), extra_args)
    }


@register.inclusion_tag('snippets/delete_action.html')
def delete_action(obj, extra_args=""):

    return {'delete_url': "%s%s" % (reverse("delete", kwargs={
        'model': get_model_name(obj),
        'pk': obj.id}), extra_args)}


@register.inclusion_tag('snippets/delete_action.html')
def inline_delete_action(obj, parent, extra_args=""):

    return {'delete_url': "%s%s" % (
        reverse("inline_delete", kwargs={
            'pk': obj.id,
            'model': get_model_name(obj),
            'parent_pk': parent.id,
            'parent_model': get_model_name(parent)}),
        extra_args)}


@register.filter
def detail_url(obj):

    return reverse('view', kwargs={'model': get_model_name(obj), 'pk': obj.id})


@register.filter
def get(iterable, idx):

    return iterable[idx]


@register.filter
def status_label(obj):

    return obj._meta.model.get_status_display(obj)


@register.filter
def status_class(status):

    if status == 1:
        return "info"
    else:
        return "warning"
