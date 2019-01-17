from django.contrib import admin
from unicorn.models.location import Location
from unicorn.models.conversion import Conversion
from unicorn.models.recipe import Recipe


class LocationAdmin(admin.ModelAdmin):

    pass


class ConversionAdmin(admin.ModelAdmin):

    pass


class MaterialsInline(admin.TabularInline):

    model = Recipe.material.through


class RecipeAdmin(admin.ModelAdmin):

    inlines = [MaterialsInline]


admin.site.register(Location, LocationAdmin)
admin.site.register(Conversion, ConversionAdmin)
admin.site.register(Recipe, RecipeAdmin)
