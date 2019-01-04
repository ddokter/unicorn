from django.template import Library
from django.urls import reverse


register = Library()


@register.filter
def ctname(obj):

    return obj.__class__.__name__.lower()


@register.inclusion_tag('snippets/listing.html', takes_context=True)
def listing(context, title, items, create_url=None):

    """ Show object listing """

    context.update({'title': title,
                    'items': items,
                    'create_url': create_url})

    return context


@register.inclusion_tag('snippets/edit_action.html')
def edit_action(obj, btn_class=""):

    return {'edit_url': reverse("edit_%s" % obj._meta.verbose_name,
                                args=[obj.id]),
            'btn_class': btn_class}


@register.inclusion_tag('snippets/add_action.html')
def add_action(model, btn_class=""):

    model_name = model._meta.verbose_name.replace(' ', '')

    return {'create_url': reverse("create_%s" % model_name),
            'btn_class': btn_class}


@register.inclusion_tag('snippets/add_action.html')
def inline_add_action(model_name, parent_id, btn_class=""):

    return {'create_url': reverse("create_%s" % model_name,
                                  kwargs={'pk': parent_id}),
            'btn_class': btn_class}


@register.inclusion_tag('snippets/delete_action.html')
def delete_action(obj, btn_class="", extra_args=""):

    return {'delete_url': "%s%s" % (
        reverse("delete_%s" % obj._meta.verbose_name, args=[obj.id]),
        extra_args), 'btn_class': btn_class}


@register.filter
def detail_url(obj):

    return reverse('view_%s' % obj._meta.verbose_name,
                   kwargs={'pk': obj.id})


@register.filter
def get(iterable, idx):

    return iterable[idx]
