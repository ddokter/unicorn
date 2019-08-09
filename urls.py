from django.urls import path, include
from django.conf import settings
from unicorn.views.home import Home
from unicorn.views.auth import LoginView, LogoutView
from unicorn.views.base import (
    ListingView, CreateView, UpdateView, DeleteView, DetailView,
    InlineCreateView, InlineDeleteView, InlineUpdateView)
from unicorn.views.recipe import (RecipeCreateView, RecipeUpdateView,
                                  RecipeConvertView, RecipeConvertModernView)
from unicorn.views.unit import UnitConvertView
from unicorn.views.conversion import (
    ConversionCreateView, ConversionUpdateView, InlineConversionCreateView,
    InlineConversionUpdateView, ConversionConvertView)


urlpatterns = [

    path('auth/', include('django.contrib.auth.urls')),

    path('login/',
         LoginView.as_view(),
         name="login"),

    path('logout/',
         LogoutView.as_view(),
         name="logout"),

    path('', Home.as_view(), name="home"),

    # Not so generic views
    #
    path('recipe/<int:pk>/convert/',
         RecipeConvertView.as_view(),
         name='convert_recipe'),

    path('recipe/<int:pk>/convert_modern/',
         RecipeConvertModernView.as_view(),
         name='convert_recipe_modern'),

    path('recipe/add/',
         RecipeCreateView.as_view(),
         name="create_recipe"),

    path('recipe/<int:pk>/edit',
         RecipeUpdateView.as_view(),
         name="edit_recipe"),

    path('conversion/add/',
         ConversionCreateView.as_view(),
         name="create_conversion"),

    path('conversion/<int:pk>/edit',
         ConversionUpdateView.as_view(),
         name="edit_conversion"),

    path('<str:parent_model>/<int:parent_pk>/add_conversion',
         InlineConversionCreateView.as_view(),
         name="inline_create_conversion"),

    path('<str:parent_model>/<int:parent_pk>/edit_conversion/<int:pk>',
         InlineConversionUpdateView.as_view(),
         name="inline_edit_conversion"),

    path('conversion/<int:pk>/convert/',
         ConversionConvertView.as_view(),
         name='convert_conversion'),

    # path('conversion/oddities/',
    #     OddConversions.as_view(),
    #     name="odd_conversions"),

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

    path('localunit/<int:pk>/convert/',
         UnitConvertView.as_view(),
         name='convert_localunit'),
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns
