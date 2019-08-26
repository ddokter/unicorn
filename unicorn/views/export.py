from django.core import serializers
from django.http import HttpResponse
from django.views.generic.detail import DetailView
from .base import GenericMixin, CTypeMixin


class ExportView(GenericMixin, DetailView, CTypeMixin):

    """ Export to JSON, using the django.core serializer """

    def get(self, request, *args, **kwargs):

        self.object = self.get_object()

        response = HttpResponse(content_type='application/json')
        response['Content-Disposition'] = 'attachment; filename="%s.json"' % (
            self.object.abbr.replace(" ", "_"))

        try:
            serializers.serialize(
                "json", self.object.list_conversions(), indent=4,
                stream=response
            )
        except:
            pass

        return response
