from django.contrib.auth.views import LoginView, LogoutView


class LoginView(LoginView):

    template_name = "login.html"
    success_url = "/"

    def get_redirect_url(self):

        return self.success_url


class LogoutView(LogoutView):

    next_page = "/"
