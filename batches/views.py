from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse, HttpResponseRedirect
from .models import Batch, Recipe, Recipe_Detail, Ingredient
from .utils import createDocket
from .forms import BatchForm, RecipeForm, RecipeDetailForm
from django.urls import reverse
from django.forms import formset_factory

def dashboard(request):
    recent_batches_list = Batch.objects.order_by('-batch_no')[0:10]
    context = {'recent_batches_list': recent_batches_list}
    return render(request, 'batches/dashboard.html', context)

def recipes(request):
    rec = Recipe.objects.filter(active=True)
    ing = Ingredient.objects.all()
    data = [{'recipe':r, 'details':r.details_as_list(ing)} for r in rec]
    context = {'recipe_data': data, 'ing_list': ing}
    return render(request, 'batches/recipes.html', context)

def ticket(request, batch_no):
    b = get_object_or_404(Batch, batch_no=batch_no)
    p = createDocket(b)
    with open(p, 'rb') as pdf:
        response = HttpResponse(pdf.read(),content_type='application/pdf')
        response['Content-Disposition'] = 'filename=b' + str(b.batch_no).zfill(8) + '.pdf'
        return response

def batch_detail(request, batch_no):
    b = get_object_or_404(Batch, batch_no=batch_no)
    context = {'batch':b}
    return render(request, 'batches/batch_detail.html', context)

def new_batch(request):
    if request.method == 'POST':
        form = BatchForm(request.POST)        
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('dashboard'))
        else:
            message = 'Batch could not be saved. Please correct errors below:'
    else:
        form = BatchForm()
        message = 'Creating New Batch'

    context = {'form':form, 'message':message}
    return render(request, 'batches/edit_batch.html', context)
 
def edit_batch(request, batch_no):
    b = get_object_or_404(Batch, batch_no=batch_no)
    if b.status != 'PEND':
        message = 'Batch may not be edited once it has been started'
        form = []
    else:
        if request.method == 'POST':
            form = BatchForm(request.POST, instance=b)    
            if form.is_valid():
                form.save()
                return HttpResponseRedirect(reverse('dashboard'))
            else:
                message = 'Batch could not be saved. Please correct errors below:'
        else:
            form = BatchForm(instance=b)
            message = 'Editing Batch No: ' + str(b)

    context = {'form':form, 'message':message, 'batch_no':batch_no}
    return render(request, 'batches/edit_batch.html', context)

def delete_batch(request, batch_no):
    b = get_object_or_404(Batch, batch_no=batch_no)
    if b.status != 'PEND':
        message = 'Batch may not be deleted once it has been started'
    else:
        if request.method == 'POST':
            b.delete()
            return HttpResponseRedirect(reverse('dashboard'))
        else:
            message = []
                   
    context = {'message':message, 'batch_no':batch_no}
    return render(request, 'batches/delete_batch.html', context)
            
def new_recipe(request):
    ing = Ingredient.objects.all()

    if request.method == 'POST':
        RecForm = RecipeForm(request.POST, prefix='recipe')
        if RecForm.is_valid():
            Rec = RecForm.save(commit=False)
            Rec.save()

            RecDetForms = dict()
            for i in ing:
                RecDet = Recipe_Detail(recipe=Rec, ingredient=i) 
                RecDetForms[str(i)] = RecipeDetailForm(request.POST, instance=RecDet, prefix=str(i))
            if all(RecDetForm.is_valid() for RecDetForm in RecDetForms.values()):
                for RecDetForm in RecDetForms.values():
                    RecDet = RecDetForm.save(commit=False)
                    if RecDet.quantity > 0: RecDet.save()
                return HttpResponseRedirect(reverse('recipes'))
            else:
                message = 'Recipe could not be saved. Please correct errors below:'
                    
        else:
            message = 'Recipe could not be saved. Please correct errors below:'
                    
    else:
        message = 'Creating New Recipe'
        RecForm = RecipeForm(prefix='recipe')
        RecDetForms = dict()
        for i in ing:
            RecDet = Recipe_Detail(ingredient=i, quantity=0) 
            RecDetForms[str(i)] = RecipeDetailForm(instance=RecDet, prefix=str(i))

    context = {'RecForm':RecForm, 'RecDetForms':RecDetForms, 'message':message}
    return render(request, 'batches/edit_recipe.html', context)

def edit_recipe(request, recipe_id):
    r = get_object_or_404(Recipe, id=recipe_id)
    if r.been_used():
        message = 'A recipe may not be edited once it has been used in batching. Please create a new recipe or copy an old recipe.'
        RecForm = []
        RecDetForms = []
    else:
        ing = Ingredient.objects.all()

        if request.method == 'POST':
            RecForm = RecipeForm(request.POST, instance=r, prefix='recipe')
            if RecForm.is_valid():
                Rec = RecForm.save(commit=False)
                Rec.save()

                RecDetForms = dict()
                for i in ing:
                    RecDetSearch = Recipe_Detail.objects.filter(recipe=Rec, ingredient=i)
                    RecDet = RecDetSearch.get() if RecDetSearch.exists() else Recipe_Detail(recipe=Rec, ingredient=i) 
                    RecDetForms[str(i)] = RecipeDetailForm(request.POST, instance=RecDet, prefix=str(i))
                if all(RecDetForm.is_valid() for RecDetForm in RecDetForms.values()):
                    for RecDetForm in RecDetForms.values():
                        RecDet = RecDetForm.save(commit=False)
                        if RecDet.quantity > 0: RecDet.save()
                    return HttpResponseRedirect(reverse('recipes'))
                else:
                    message = 'Recipe could not be saved. Please correct errors below:'                    
            else:
                message = 'Recipe could not be saved. Please correct errors below:'
                        
        else:
            message = 'Editing Recipe: ' + str(r.id) + ' - ' + str(r.name)
            RecForm = RecipeForm(instance=r, prefix='recipe')
            RecDetForms = dict()
            for i in ing:
                RecDetSearch = Recipe_Detail.objects.filter(recipe=r, ingredient=i)
                RecDet = RecDetSearch.get() if RecDetSearch.exists() else Recipe_Detail(recipe=r, ingredient=i, quantity=0)
                RecDetForms[str(i)] = RecipeDetailForm(instance=RecDet, prefix=str(i))

    context = {'RecForm':RecForm, 'RecDetForms':RecDetForms, 'message':message, 'recipe_id':recipe_id}
    return render(request, 'batches/edit_recipe.html', context)

def delete_recipe(request, recipe_id):
    r = get_object_or_404(Recipe, id=recipe_id)
    if r.been_used():
        message = 'Recipe may not be deleted once it has been used.'
    else:
        if request.method == 'POST':
            r.delete()
            return HttpResponseRedirect(reverse('recipes'))
        else:
            message = []
                   
    context = {'message':message, 'recipe_id':recipe_id}
    return render(request, 'batches/delete_recipe.html', context)

def copy_recipe(request, recipe_id):
    r = get_object_or_404(Recipe, id=recipe_id)
    rds = r.recipe_detail_set.all()
    r.pk = None
    r.name = r.name + '-Copy'
    r.save()
    for rd in rds:
        rd.pk = None
        rd.recipe = r
        rd.save()
    return HttpResponseRedirect(reverse('recipes'))
            
