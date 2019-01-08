from django.urls import path
from unicorn.views.home import Home
from unicorn.views.base import (ListingView, CreateView, UpdateView,
                                DeleteView, DetailView, InlineCreateView,
                                InlineDeleteView, InlineUpdateView)
from unicorn.views.convert import ConvertView
from unicorn.views.expression import ExpressionCreateView
from unicorn.views.recipe import (RecipeCreateView, RecipeUpdateView,
                                  RecipeConvertView)
from unicorn.models.conversion import Conversion
from unicorn.models.expression import SubConversion
from unicorn.models.unit import Unit


urlpatterns = [
    path('', Home.as_view(), name="home"),

    path('convert/', ConvertView.as_view(), name="convert"),

    # Generic delete view
    #
    path('<str:model>/<int:pk>/delete',
         DeleteView.as_view(),
         name="delete"),

    # Generic listing
    #
    path('<str:model>/list',
         ListingView.as_view(),
         name="list"),

    # Generic detail view
    #
    path('<str:model>/<int:pk>',
         DetailView.as_view(),
         name="view"),

    # Generic add view
    #
    path('<str:model>/add/',
         CreateView.as_view(),
         name="create"),

    # Generic edit view
    #
    path('<str:model>/<int:pk>/edit',
         UpdateView.as_view(),
         name="edit"),

    # Generic inline add
    #
    path('<str:parent_model>/<int:parent_pk>/add_<str:model>',
         InlineCreateView.as_view(),
         name="inline_create"),

    # Generic inline edit
    #
    path('<str:parent_model>/<int:parent_pk>/edit_<str:model>/<int:pk>',
         InlineUpdateView.as_view(),
         name="inline_edit"),

    # Generic inline delete
    #
    path('<str:parent_model>/<int:parent_pk>/rm_<str:model>/<int:pk>',
         InlineDeleteView.as_view(),
         name="inline_delete"),

    path('expression/<int:pk>/add',
         ExpressionCreateView.as_view(model=SubConversion),
         name="create_expression"),
    path('expressions/<int:pk>/edit',
         UpdateView.as_view(model=SubConversion),
         name="edit_expression"),

    path('recipes/<int:pk>/convert/',
         RecipeConvertView.as_view(),
         name='convert_recipe'),
    path('recipes/add/',
         RecipeCreateView.as_view(),
         name="create_recipe"),
    path('recipes/<int:pk>/edit',
         RecipeUpdateView.as_view(),
         name="edit_recipe"),

]
