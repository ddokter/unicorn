from django.urls import reverse
from .base import CreateView


class ExpressionCreateView(CreateView):

    def get_initial(self):

        return {'conversion': self.kwargs.get('pk', None)}

    @property
    def success_url(self):

        return reverse("view", kwargs={'pk': self.kwargs.get('pk', None)})

    @property
    def cancel_url(self):

        return self.success_url

    @property
    def action_url(self):

        return reverse("create_expression",
                       kwargs={'pk': self.kwargs.get('pk', None)})
