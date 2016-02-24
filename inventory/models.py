from django.db import models
from datetime import date as dm
from django.core.mail import send_mail


def checkStock(minimum = 10):
    for item in Item.objects.all():
        if item.supply < minimum:
            warning = "Warning: %s stock at %d, buy summore!" % (item.name, item.supply)
#            send_mail('Stock warning', warning, 'info@noztek.com',
#                      ['info@noztek.com'], fail_silently=False)
            print warning

# Basic objects, without relationships
class Location(models.Model):
    location = models.CharField(max_length=100)
    
    def __unicode__(self):
        return self.location

class Owner(models.Model):
    name = models.CharField('Owner name', max_length=50)
    contact = models.CharField('Owner contact', max_length = 100, blank = True)

    def __unicode__(self):
        return self.name

class Supplier(models.Model):
    name = models.CharField(max_length = 50)
    website = models.URLField(max_length = 100)
    email = models.EmailField(blank = True)
    phone = models.CharField(max_length = 20, blank = True)

    def __unicode__(self):
        return self.name

class Customer(models.Model):
    name = models.CharField(max_length = 50)
    email = models.EmailField(blank = True)
    phone = models.CharField(max_length = 20, blank = True)

    def __unicode__(self):
        return self.name

class Item(models.Model):
    name = models.CharField('Item name', max_length=100)
    desc = models.CharField('Description of item', max_length=400, blank = True)
    supply = models.IntegerField(default = 0)
    suppliers = models.ManyToManyField(Supplier, through='ItemSupplier')
    locations = models.ManyToManyField(Location, through='ItemLocation')

    def __unicode__(self):
        return self.name

class Product(models.Model):
    name = models.CharField('Item name', max_length=100)
    desc = models.CharField('Description of item', max_length=400, blank = True)
    # supply = models.IntegerField(default = 0)
    # to_make = models.IntegerField(default = 0)
    req_item = models.ManyToManyField(Item, through='ItemRequirement')

    def __unicode__(self):
        return self.name

#TODO: Can we make it so that if a Stock order is deleted, we can also reduce associated stock?
#      Maybe more complicated than it needs to be, we could just use breakage
class StockOrder(models.Model):
    supplier = models.ForeignKey(Supplier)
    date = models.DateTimeField('Date Ordered')
    delivery_date = models.DateField('Delivery Date')
#    date.auto_now_add
    items_ordered = models.ManyToManyField(Item, through='ItemOrder')
    delivered = models.BooleanField('Delivered?', default = False)
    def save(self, *args, **kwargs):
        if self.pk:
            orig = StockOrder.objects.get(pk = self.pk)
            if orig.delivered != self.delivered:
                if self.delivered:
                    for entry in self.items_ordered.all():
                        entry.supply += ItemOrder.objects.filter(stock_order__date=self.date).filter(item__name=entry.name)[0].number_ordered
                        entry.save()
                else:
                    for entry in self.items_ordered.all():
                        entry.supply -= ItemOrder.objects.filter(stock_order__date=self.date).filter(item__name=entry.name)[0].number_ordered
                        entry.save()
        if not self.pk and self.delivered:
            super(StockOrder, self).save(*args, **kwargs)
            for entry in self.items_ordered.all():
                entry.supply += ItemOrder.objects.filter(stock_order__date=self.date).filter(item__name=entry.name)[0].number_ordered
                entry.save() 
        super(StockOrder, self).save(*args, **kwargs)
        checkStock()

    def __unicode__(self):
        return self.supplier.name

class StockCorrection(models.Model):
    warning = models.CharField(max_length = 256, default = "Warning: this can only be applied once. Changing values after creation will have no effect - don't do it!")
    date = models.DateTimeField('Date Ordered')
    items_changed = models.ManyToManyField(Item, through='StockChange')
    reason = models.CharField(max_length = 256)
    def save(self, *args, **kwargs):
        if not self.pk:
            super(StockCorrection, self).save(*args, **kwargs)
            for entry in self.items_changed.all():
                #BUG: Does not get any entries
                print "HERE"
                print entry.supply
                entry.supply += StockChange.objects.filter(correction__date=self.date).filter(correction__reason=self.reason).filter(item__name=entry.name)[0].number_changed
                print entry.supply
                entry.save() 
        super(StockCorrection, self).save(*args, **kwargs)
        checkStock()

    def __unicode__(self):
        return str(self.date)

class ProductOrder(models.Model):
    customer = models.ForeignKey(Customer)
    product = models.ForeignKey(Product)
    date = models.DateTimeField('Date Ordered')
    completion_date = models.DateField('Completion Date')
#    items_used = models.ManyToManyField(Item, through='ItemOrder')
    completed = models.BooleanField('Completed?', default = False)
    def save(self, *args, **kwargs):
        if not self.pk and self.completed:
            for entry in self.product.req_item.all():
                entry.supply -= ItemRequirement.objects.filter(product__name=self.product.name).filter(item__name=entry.name)[0].number_required
                entry.save()
        if self.pk:
            orig = ProductOrder.objects.get(pk = self.pk)
            if orig.completed != self.completed:
                if self.completed:
                    for entry in self.product.req_item.all():
                        entry.supply -= ItemRequirement.objects.filter(product__name=self.product.name).filter(item__name=entry.name)[0].number_required
                        entry.save()
                else:
                    for entry in self.product.req_item.all():
                        entry.supply += ItemRequirement.objects.filter(product__name=self.product.name).filter(item__name=entry.name)[0].number_required
                        entry.save()
           
        super(ProductOrder, self).save(*args, **kwargs)
        checkStock()

    def __unicode__(self):
        return self.product.name

# class CustomerOrder(models.Model):
#     customer = models.ForeignKey(Customer)
#     product = models.ManyToManyField(Product, through='ProductRequirement')
#     date = models.DateTimeField('Date Ordered')
#     completion_date = models.DateField('Completion Date')
# #    items_used = models.ManyToManyField(Item, through='ItemOrder')
#     completed = models.BooleanField('Completed?', default = False)
#     def save(self, *args, **kwargs):
#         if self.pk:
#             orig = ProductOrder.objects.get(pk = self.pk)
#             if orig.completed != self.completed:
#                 if self.completed:
#                     for entry in self.product.req_item.all():
#                         entry.supply -= ItemRequirement.objects.filter(product__name=self.product.name).filter(item__name=entry.name)[0].number_required
#                         entry.save()
#                 else:
#                     for entry in self.product.req_item.all():
#                         entry.supply += ItemRequirement.objects.filter(product__name=self.product.name).filter(item__name=entry.name)[0].number_required
#                         entry.save()
           
#         super(ProductOrder, self).save(*args, **kwargs)

#     def __unicode__(self):
#         return self.product.name

# Relationship objects
class ItemOrder(models.Model):
    stock_order = models.ForeignKey(StockOrder)
    item = models.ForeignKey(Item)
    number_ordered = models.IntegerField(default = 0)

    def number_stocked(self):
        if self.item == None: return "undefined"
        return self.item.supply

    def __unicode__(self):
        return self.stock_order.supplier.name

class StockChange(models.Model):
    correction = models.ForeignKey(StockCorrection)
    item = models.ForeignKey(Item)
    number_changed = models.IntegerField(default = 0)

    def number_stocked(self):
        if self.item == None: return "undefined"
        return self.item.supply

    def __unicode__(self):
        return self.correction.reason

class ItemRequirement(models.Model):
    product = models.ForeignKey(Product)
    item = models.ForeignKey(Item)
    number_required = models.IntegerField(default = 0)
   
    def number_stocked(self):
        if self.item == None: return "undefined"
        return self.item.supply

    def __unicode__(self):
        return self.item.name

class ItemLocation(models.Model):
    item = models.ForeignKey(Item)
    location = models.ForeignKey(Location)
    date_moved = models.DateField()
    number_stored = models.IntegerField(default = 0)

    def __unicode__(self):
        return self.location.location

class ItemSupplier(models.Model):
    item = models.ForeignKey(Item)
    supplier = models.ForeignKey(Supplier)
    link = models.URLField('Link to item page', max_length=100, blank = True)
    part = models.CharField('Part No.', max_length=50, blank = True)
    ppu = models.FloatField('Price per unit')
    max_del = models.CharField('Max delivery time', max_length=100, blank = True)

    def __unicode__(self):
        return self.supplier.name
