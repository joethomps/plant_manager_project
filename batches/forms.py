from django import forms
from batches.models import Batch, Recipe, Recipe_Detail, Client, Truck, Driver

class BatchForm(forms.ModelForm):
    class Meta:
        model = Batch
        exclude = ['batch_no', 'ticket_created', 'status']

class RecipeForm(forms.ModelForm):
    class Meta:
        model = Recipe
        fields = ['name', 'description', 'slump_class', 'exposure_class', 'cl_content_class']

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
    
