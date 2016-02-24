from django.db import models
from datetime import date as dm
#Extended from Letsmake inventory app

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
    supply = models.IntegerField(default = 0)
    to_make = models.IntegerField(default = 0)
    req_item = models.ManyToManyField(Item, through='ItemRequirement')

    def __unicode__(self):
        return self.name

class StockOrder(models.Model):
    supplier = models.ForeignKey(Supplier)
    date = models.DateTimeField('Date Ordered', default = dm.today)
    delivery_date = models.DateField('Delivery Date', default = dm.today)
#    date.auto_now_add
    items_ordered = models.ManyToManyField(Item, through='ItemOrder')
    delivered = models.BooleanField('Delivered?', default = False)
    def save(self):
        if self.delivered:
            for entry in self.items_ordered.all():
                entry.supply += ItemOrder.objects.filter(stock_order__date=self.date).filter(item__name=entry.name)[0].number_ordered
                entry.save()

    def __unicode__(self):
        return self.supplier.name

#todo: product order
#todo: breakage

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
