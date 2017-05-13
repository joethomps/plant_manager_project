from django.contrib import admin

from .models import Client, Recipe, Driver, Ingredient, Location, Truck, Batch, Drop, Drop_Detail, Recipe_Detail

class RecipeDetailInline(admin.TabularInline):
    model = Recipe_Detail
    extra = 3

class RecipeAdmin(admin.ModelAdmin):
    fieldsets = [
        (None,               {'fields': ['name','description','active']}),
        ('Specification Information', {'fields': ['slump_class', 'exposure_class', 'cl_content_class']})]
    inlines = [RecipeDetailInline]
    list_display = ('name', 'description')

class LocationAdmin(admin.ModelAdmin):
    list_display = ('name','plc_ref','description','current_ingredient','usage_ratio')
    ordering = ['plc_ref']

admin.site.register(Client)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Driver)
admin.site.register(Ingredient)
admin.site.register(Location, LocationAdmin)
admin.site.register(Truck)
admin.site.register(Batch)
admin.site.register(Drop)
admin.site.register(Drop_Detail)
admin.site.register(Recipe_Detail)
