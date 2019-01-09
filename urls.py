from django.urls import path
from unicorn.views.home import Home
from unicorn.views.base import (
    ListingView, CreateView, UpdateView, DeleteView, DetailView,
    InlineCreateView, InlineDeleteView, InlineUpdateView)
from unicorn.views.recipe import (RecipeCreateView, RecipeUpdateView,
                                  RecipeConvertView)
from unicorn.views.unit import UnitConvertView


urlpatterns = [
    path('', Home.as_view(), name="home"),

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

    path('unit/<int:pk>/convert/',
         UnitConvertView.as_view(),
         name='convert_unit'),

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
