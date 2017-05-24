from django.db import models
from django.utils import timezone
from django.db.models import Max, Sum, Avg, F

class Client(models.Model):
    name = models.CharField(max_length=50)
    def can_edit(self):
        return (False, 'Cannot edit client once it has been used in a batch') if self.used() else (True, '')
    def __str__(self):
        return self.name

class Recipe(models.Model):
    STRENGTH_CLASS_CHOICES = (
        ('10', 'C8/10'),('15', 'C12/15'),('20', 'C16/20'),('25', 'C20/25'),('30', 'C25/30'),
        ('35', 'C28/35'),('37', 'C30/37'),('40', 'C32/40'),('45', 'C35/45'),('50', 'C40/50'),
        ('55', 'C45/55'),('60', 'C50/60'),('67', 'C55/67'),('75', 'C60/75'),('85', 'C70/85'),
        ('95', 'C80/95'),('105', 'C90/105'),('115','C100/115')
    )
    EXPOSURE_CLASS_CHOICES = (
        ('XO', 'XO'),
        ('XC1', 'XC1'),('XC2', 'XC2'),('XC3', 'XC3'),('XC4', 'XC4'),
        ('XS1', 'XS1'),('XS2', 'XS2'),('XS3', 'XS3'),('XS4', 'XS4'),
        ('XD1', 'XD1'),('XD2', 'XD2'),('XD3', 'XD3'),('XD4', 'XD4'),
        ('XF1', 'XF1'),('XF2', 'XF2'),('XF3', 'XF3'),
        ('XA1', 'XA1'),('XA2', 'XA2'),('XA3', 'XA3'),
    )
    SLUMP_CLASS_CHOICES = (
        ('S1', 'S1 (10-40mm)'),
        ('S2', 'S2 (50-90mm)'),
        ('S3', 'S3 (100-150mm)'),
        ('S4', 'S4 (160-210mm)'),
        ('S5', 'S5 (>=220mm)')
    )
    CL_CONTENT_CLASS_CHOICES = (
        ('C1 1,0','C1 1,0'),
        ('C1 0,40','C1 0,40'),
        ('C1 0,20','C1 0,20'),
        ('C1 0,10','C1 0,10'),
    )
    def next_recipe_no():
        max = Recipe.objects.all().aggregate(Max('recipe_no'))['recipe_no__max']
        if max == None:
            return 1
        else:
            return max+1
    recipe_no = models.IntegerField(default=next_recipe_no)
    name = models.CharField(max_length=50)
    create_time = models.DateTimeField(default=timezone.now)
    description = models.CharField(max_length=200, blank=True)
    strength_class = models.CharField(max_length=2, choices=STRENGTH_CLASS_CHOICES, blank=True)
    slump_class = models.CharField(max_length=2, choices=SLUMP_CLASS_CHOICES, blank=True)
    exposure_class = models.CharField(max_length=3, choices=EXPOSURE_CLASS_CHOICES, blank=True)
    cl_content_class = models.CharField(max_length=7, choices=CL_CONTENT_CLASS_CHOICES, blank=True)
    mix_time = models.IntegerField(default=180)
    active = models.BooleanField(default=True)
    version = models.IntegerField(default=1)
    def used(self):
        return self.batch_set.exists()
    def details_as_list(self, ing_list, include_zeros=True):
        rds = self.recipe_detail_set
        details = []
        for i in ing_list:
            rd = rds.filter(ingredient=i)
            if rd.exists():
                details.append(rd.get().quantity)
            elif include_zeros:
                details.append(0)
        return details
    def admixtures_as_list(self):
        rds = Recipe_Detail.objects.filter(recipe=self, ingredient__category='ADD')
        return ['%s: %.2f %s/m^3' % (rd.ingredient, rd.quantity, rd.ingredient.unit) for rd in rds]   
    def cement_types_as_list(self):
        rds = Recipe_Detail.objects.filter(recipe=self, ingredient__category='CEM')
        cems = Ingredient.objects.filter(id__in=rds.values('ingredient_id'))
        return [c.cement_type for c in cems]
    def exp_classes_as_list(self):
        return [self.exposure_class]
    def total_cat(self, category):
        rds = Recipe_Detail.objects.filter(recipe=self, ingredient__category=category)
        return rds.aggregate(Sum('quantity'))['quantity__sum'] if rds.exists() else 0
    def total_aggregate(self):
        return self.total_cat('AGG')
    def total_cement(self):
        return self.total_cat('CEM')
    def total_water(self):
        return self.total_cat('WAT')
    def aggregate_D(self):
        rds = Recipe_Detail.objects.filter(recipe=self, ingredient__category='AGG')
        aggs = Ingredient.objects.filter(id__in=rds.values('ingredient_id'))
        return aggs.aggregate(Max('agg_size'))['agg_size__max'] if aggs.exists() else 0
    def wc_ratio(self):
        return self.total_water()/self.total_cement() 
    def __str__(self):
        return '%s_%i.%i' % (self.name, self.recipe_no, self.version)

class Driver(models.Model):
    name = models.CharField(max_length=50)
    def used(self):
        return self.batch_set.exists()
    def can_edit(self):
        return (False, 'Cannot edit driver once it has been used in a batch') if self.used() else (True, '')
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
    CEM_TYPE_CHOICES = (
        ('CEM I N', 'CEM I N'),
        ('CEM I R', 'CEM I R'),
        ('CEM I SR', 'CEM I SR'),
    )
    name = models.CharField(max_length=50)
    category = models.CharField(max_length=3,choices=INGREDIENT_TYPE_CHOICES,default='OTH')
    description = models.CharField(max_length=200, blank=True)
    unit = models.CharField(max_length=10, blank=True)
    agg_size = models.IntegerField(default=0,blank=True)
    cement_type = models.CharField(max_length=10, choices=CEM_TYPE_CHOICES,blank=True)
    def used(self):
        return self.drop_detail_set.exists()
    def can_edit(self):
        return (False, 'Cannot edit ingredient once it has been used in a batch') if self.used() else (True, '')
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
    def can_edit(self):
        return (False, 'Cannot edit client once it has been used in a batch') if self.used() else (True, '')
    def __str__(self):
        return self.reg

class Batch(models.Model):
    def next_batch_no():
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
    batch_no = models.IntegerField(default=next_batch_no)
    create_time = models.DateTimeField(default=timezone.now)
    client = models.ForeignKey(Client, on_delete=models.PROTECT)
    recipe = models.ForeignKey(Recipe, on_delete=models.PROTECT,limit_choices_to={'active': True})
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
    def start_datetime(self):
        if self.drop_set.exists():
            ds = self.drop_set.order_by('no_in_batch')
            return ds[0].start_datetime
        else:
            return None
    def end_datetime(self):
        if self.drop_set.exists():
            ds = self.drop_set.order_by('no_in_batch')
            n = ds.count();
            return ds[n-1].end_datetime
        else:
            return None
    def batch_totals(self, include_zeros=False):
        dds = Drop_Detail.objects.filter(drop__batch=self)
        totals = []
        for i in Ingredient.objects.all():        
            dd = dds.filter(ingredient=i)
            total = {'ingredient':i}
            if dd.exists():
                aggs = dd.aggregate(design=Sum('design'), target=Sum('target'), actual=Sum('actual'),water=Sum(F('moisture')*F('actual')))
                total.update(aggs)
                if total['actual'] > 0:
                    total['moisture'] = total['water']/total['actual']
                totals.append(total)
            elif include_zeros:
                total.update({'design':0, 'target':0, 'actual':0, 'water':0, 'moisture':0})
                totals.append(total)
        return totals      
    def __str__(self):
        return str(self.batch_no).zfill(6)
    
class Drop(models.Model):
    drop_no = models.IntegerField()
    batch = models.ForeignKey(Batch, on_delete=models.CASCADE)
    no_in_batch = models.IntegerField()
    volume = models.DecimalField(max_digits=4, decimal_places=2)
    start_datetime = models.DateTimeField()
    end_datetime = models.DateTimeField()
    def __str__(self):
        return str(self.batch) + '_' + str(self.no_in_batch)
    
class Drop_Detail(models.Model):
    drop = models.ForeignKey(Drop, on_delete=models.CASCADE)
    ingredient = models.ForeignKey(Ingredient, on_delete=models.PROTECT)
    used_location = models.ForeignKey(Location, on_delete=models.PROTECT)
    design = models.DecimalField(max_digits=6, decimal_places=2)
    target = models.DecimalField(max_digits=6, decimal_places=2)
    actual = models.DecimalField(max_digits=6, decimal_places=2)
    moisture = models.DecimalField(max_digits=6, decimal_places=2)
    def __str__(self):
        return str(self.drop) + '_' + str(self.actual) + '_' + str(self.ingredient)
    
class Recipe_Detail(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    ingredient = models.ForeignKey(Ingredient, on_delete=models.PROTECT)
    quantity = models.DecimalField(max_digits=6, decimal_places=2)
    def __str__(self):
        return str(self.recipe) + '_' + str(self.quantity) + '_' + str(self.ingredient)
    
