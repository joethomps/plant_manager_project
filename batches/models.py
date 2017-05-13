from django.db import models
from django.utils import timezone

class Client(models.Model):
    name = models.CharField(max_length=50)
    def __str__(self):
        return self.name

class Recipe(models.Model):
    name = models.CharField(max_length=50)
    description = models.CharField(max_length=200, blank=True)
    slump_class = models.CharField(max_length=10, blank=True)
    exposure_class = models.CharField(max_length=10, blank=True)
    cl_content_class = models.CharField(max_length=10, blank=True)
    active = models.BooleanField(default=True)
    def been_used(self):
        bs = self.batch_set.all()
        return True if bs.exists() else False
    def details_as_list(self, ing_list):
        det = []
        for i in ing_list:
            rd = self.recipe_detail_set.filter(ingredient=i)
            det.append(rd.get().quantity if rd.exists() else 0)
        return det
    def __str__(self):
        return self.name

class Driver(models.Model):
    name = models.CharField(max_length=50)
    def __str__(self):
        return self.name

class Ingredient(models.Model):
    INGREDIENT_TYPE_CHOICES = (
        ('AGG', 'Aggregate'),
        ('CEM', 'Cement'),
        ('ADD', 'Additive'),
        ('WAT', 'Water'),
        ('OTH', 'Other'),
    )
    name = models.CharField(max_length=50)
    category = models.CharField(max_length=3,choices=INGREDIENT_TYPE_CHOICES,default='AGG')
    description = models.CharField(max_length=200, blank=True)
    unit = models.CharField(max_length=10, blank=True)
    agg_size = models.IntegerField(default=0,blank=True)
    def __str__(self):
        return self.name

class Location(models.Model):
    plc_ref = models.IntegerField(unique=True)
    name = models.CharField(max_length=50, default='')
    description = models.CharField(max_length=50, blank=True)
    current_ingredient = models.ForeignKey(Ingredient, on_delete=models.SET_NULL, null=True)
    usage_ratio = models.IntegerField(default=1)
    def __str__(self):
        return self.name

class Truck(models.Model):
    reg = models.CharField(max_length=15)
    def __str__(self):
        return self.reg

class Batch(models.Model):
    def next_batch_no():
        from django.db.models import Max
        max = Batch.objects.all().aggregate(Max('batch_no'))['batch_no__max']
        if max == None:
            return 100
        else:
            return max+1
    BATCH_STATUS_CHOICES = (
    ('PEND', 'Pending'),
    ('STAR', 'Started'),
    ('COMP', 'Completed'),
    ('ABOR', 'Aborted'),
    )
    batch_no = models.IntegerField(default=next_batch_no, editable=False)
    create_time = models.DateTimeField(default=timezone.now, editable=False)
    client = models.ForeignKey(Client, on_delete=models.PROTECT)
    recipe = models.ForeignKey(Recipe, on_delete=models.PROTECT)
    truck = models.ForeignKey(Truck, on_delete=models.PROTECT)
    driver = models.ForeignKey(Driver, on_delete=models.PROTECT)
    volume = models.DecimalField(max_digits=4, decimal_places=2)
    deliv_addr_1 = models.CharField(max_length=50, blank=True)
    deliv_addr_2 = models.CharField(max_length=50, blank=True)
    deliv_addr_3 = models.CharField(max_length=50, blank=True)
    deliv_addr_4 = models.CharField(max_length=50, blank=True)
    eircode = models.CharField(max_length=7, blank=True)
    order_ref = models.CharField(max_length=50, blank=True)
    notes = models.CharField(max_length=200, blank=True)
    status = models.CharField(max_length=4, choices=BATCH_STATUS_CHOICES, default='PEND')
    ticket_created = models.BooleanField(default=False)
    def __str__(self):
        return str(self.batch_no).zfill(8)
    
class Drop(models.Model):
    drop_no = models.IntegerField()
    batch = models.ForeignKey(Batch, on_delete=models.CASCADE)
    no_in_batch = models.IntegerField()
    volume = models.DecimalField(max_digits=4, decimal_places=2)
    start_datetime = models.DateTimeField()
    end_datetime = models.DateTimeField()
    def __str__(self):
        return str(self.drop_no) + ' (' + str(self.batch) + ' - ' + str(self.no_in_batch) + ')'
    
class Drop_Detail(models.Model):
    drop = models.ForeignKey(Drop, on_delete=models.CASCADE)
    ingredient = models.ForeignKey(Ingredient, on_delete=models.PROTECT)
    used_location = models.ForeignKey(Location, on_delete=models.PROTECT)
    design = models.IntegerField()
    target = models.IntegerField()
    actual = models.IntegerField()
    moisture = models.IntegerField()
    def __str__(self):
        return str(self.drop)+' - '+str(self.ingredient)
    
class Recipe_Detail(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    ingredient = models.ForeignKey(Ingredient, on_delete=models.PROTECT)
    quantity = models.IntegerField()
    def __str__(self):
        return str(self.recipe) + ' - ' + str(self.ingredient)
    
