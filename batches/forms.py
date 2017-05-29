from django import forms
from batches.models import Batch, Recipe, Recipe_Detail, Client, Truck, Driver, Location, Ingredient

class BatchForm(forms.ModelForm):
    class Meta:
        model = Batch
        exclude = ['batch_no', 'create_time', 'ticket_created', 'status']

class RecipeForm(forms.ModelForm):
    class Meta:
        model = Recipe
        fields = ['name', 'description', 'strength_class', 'slump_class', 'exposure_class','exposure_class_2','exposure_class_3','exposure_class_4','exposure_class_5','exposure_class_6', 'cl_content_class', 'mix_time']

class RecipeDetailForm(forms.ModelForm):
    class Meta:
        model = Recipe_Detail
        fields = ['quantity']
        
class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        exclude = []

class TruckForm(forms.ModelForm):
    class Meta:
        model = Truck
        exclude = []

class DriverForm(forms.ModelForm):
    class Meta:
        model = Driver
        exclude = []

class IngredientForm(forms.ModelForm):
    class Meta:
        model = Ingredient
        fields = ['name', 'description', 'category', 'agg_size', 'cement_type', 'unit']

class LocationForm(forms.ModelForm):
    class Meta:
        model = Location
        fields = ['current_ingredient', 'usage_ratio']
        
