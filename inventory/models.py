from django.db import models
from datetime import date as dm
from django.core.mail import send_mail
from django.db.models.signals import post_save
from django.dispatch import receiver
import datetime

USE_EMAIL = True

#TODO add a on-delete function to stockorder and product order that puts items back in stock

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
    address = models.CharField(max_length = 500, blank = True)

    def __unicode__(self):
        return self.name

class Assembler(models.Model):
    name = models.CharField(max_length = 50)
    website = models.URLField(max_length = 100, blank = True)
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
    minimum = models.IntegerField('Minimum stock warning', default = 5)

    def __unicode__(self):
        return self.name

class Product(models.Model):
    name = models.CharField('Item name', max_length=100)
    desc = models.CharField('Description of item', max_length=400, blank = True)
    req_item = models.ManyToManyField(Item, through='ItemRequirement')

    def number_stocked(self):
        if self.name == None: return "undefined"
        stock = 0
        for assembly in ProductAssembly.objects.filter(product__name=self.name):
            if assembly.completed:
                stock += assembly.number_ordered
        for order in ProductRequirement.objects.filter(product__name=self.name):
            if order.completed:
                stock -= order.number_ordered
        return stock

    # class Meta:
    #     verbose_name_plural = 'Product specifications'

    def __unicode__(self):
        return self.name

class CustomerOrder(models.Model):
    customer = models.ForeignKey(Customer)
    product = models.ManyToManyField(Product, through='ProductRequirement')
    additional_items = models.ManyToManyField(Item, through='AdditionalItem')
    date = models.DateTimeField('Date Ordered')
    completion_date = models.DateField('Completion Date', default = datetime.date.today)
    tracking = models.URLField('Tracking URL:', max_length=300, blank = True)

    def complete(self):
        if self.pk == None: return "undefined"
        completed = True
        for prod in ProductRequirement.objects.filter(customer_order__pk = self.pk):
            if not prod.completed:
                completed = False
        return completed
    complete.boolean = True

    def __unicode__(self):
        return self.customer.name

class AssemblyOrder(models.Model):
    product = models.ManyToManyField(Product, through='ProductAssembly')
    assembler = models.ForeignKey(Assembler)
    date = models.DateTimeField('Date sent')
    due_date = models.DateField('Due date', default = datetime.date.today)

    def complete(self):
        if self.pk == None: return "undefined"
        completed = True
        for prod in ProductAssembly.objects.filter(assembly_order__pk = self.pk):
            if not prod.completed:
                completed = False
        return completed
    complete.boolean = True

    def __unicode__(self):
        return self.assembler.name

# Relationship objects
class ProductAssembly(models.Model):
    assembly_order = models.ForeignKey(AssemblyOrder)
    product = models.ForeignKey(Product)
    number_ordered = models.IntegerField(default = 1)
    completion_date = models.DateField('Completion Date', default=datetime.date.today)
    completed = models.BooleanField('Completed?', default = False)

    def number_stocked(self):
        if self.product == None: return "undefined"
        stock = 0
        for assembly in ProductAssembly.objects.filter(product__name=self.product.name):
            if assembly.completed:
                stock += assembly.number_ordered
        for order in ProductRequirement.objects.filter(product__name=self.product.name):
            if order.completed:
                stock -= order.number_ordered
        return stock

    def adjustStock(self):
        restock = []
        if not self.pk:
            for entry in self.product.req_item.all():
                entry.supply -= ItemRequirement.objects.filter(product__name=self.product.name).filter(item__name=entry.name)[0].number_required*self.number_ordered
                entry.save()
                if entry.supply < entry.minimum:
                    restock.append((entry.name, entry.supply))
        if len(restock) > 0:
            warning = ""
            for name, supply in restock:
                warning += "Warning: %s stock at %d!\n" % (name, supply)
            print warning
            if USE_EMAIL:
                send_mail('Stock warning', warning, 'noztek.inventory@gmail.com',
                        ['info@noztek.com'], fail_silently=True)
                send_mail('Stock warning', warning, 'noztek.inventory@gmail.com',
                        ['nseymoursmith@gmail.com'], fail_silently=True)

    def save(self, *args, **kwargs):
        self.adjustStock()
        super(ProductAssembly, self).save(*args, **kwargs)

    def __unicode__(self):
        return self.product.name

class ProductRequirement(models.Model):
    customer_order = models.ForeignKey(CustomerOrder)
    product = models.ForeignKey(Product)
    number_ordered = models.IntegerField(default = 1)
    completion_date = models.DateField('Completion Date', default=datetime.date.today)
    self_built = models.BooleanField(default = False)
    completed = models.BooleanField('Completed?', default = False)

    def number_stocked(self):
        if self.product == None: return "undefined"
        stock = 0
        for assembly in ProductAssembly.objects.filter(product__name=self.product.name):
            if assembly.completed:
                stock += assembly.number_ordered
        for order in ProductRequirement.objects.filter(product__name=self.product.name):
            if order.completed and not order.self_built:
                stock -= order.number_ordered
        return stock

    def adjustStock(self):
        restock = []
        if not self.pk and self.self_built:
            for entry in self.product.req_item.all():
                entry.supply -= ItemRequirement.objects.filter(product__name=self.product.name).filter(item__name=entry.name)[0].number_required*self.number_ordered
                entry.save()
                if entry.supply < entry.minimum:
                    restock.append((entry.name, entry.supply))
        if self.pk:
            orig = ProductRequirement.objects.get(pk = self.pk)
            if orig.self_built != self.self_built:
                if self.self_built:
                    for entry in self.product.req_item.all():
                        entry.supply -= ItemRequirement.objects.filter(product__name=self.product.name).filter(item__name=entry.name)[0].number_required*self.number_ordered
                        entry.save()
                        if entry.supply < entry.minimum:
                            restock.append((entry.name, entry.supply))
                else:
                    for entry in self.product.req_item.all():
                        entry.supply += ItemRequirement.objects.filter(product__name=self.product.name).filter(item__name=entry.name)[0].number_required*self.number_ordered
                        entry.save()
                        if entry.supply < entry.minimum:
                            restock.append((entry.name, entry.supply))
        if len(restock) > 0:
            warning = ""
            for name, supply in restock:
                warning += "Warning: %s stock at %d!\n" % (name, supply)
            print warning
            if USE_EMAIL:
                send_mail('Stock warning', warning, 'noztek.inventory@gmail.com',
                        ['info@noztek.com'], fail_silently=True)
                send_mail('Stock warning', warning, 'noztek.inventory@gmail.com',
                        ['nseymoursmith@gmail.com'], fail_silently=True)

    def save(self, *args, **kwargs):
        self.adjustStock()
        super(ProductRequirement, self).save(*args, **kwargs)

    def __unicode__(self):
        return self.product.name

class AdditionalItem(models.Model):
    customer_order = models.ForeignKey(CustomerOrder)
    item = models.ForeignKey(Item)
    number_ordered = models.IntegerField(default = 1)
    added = models.BooleanField('Added to order?', default = False)

    def adjustStock(self):
        restock = []
        if not self.pk and self.added:
            self.item.supply -= self.number_ordered
            self.item.save()
        #check working 
        if self.pk:
            orig = AdditionalItem.objects.get(pk = self.pk)
            if orig.added != self.added:
                if self.added:
                    self.item.supply -= self.number_ordered
                    self.item.save()
                    if self.item.supply < self.item.minimum:
                        restock.append((self.item.name, self.item.supply))
                else:
                    self.item.supply += self.number_ordered
                    self.item.save()
                    if self.item.supply < self.item.minimum:
                        restock.append((self.item.name, self.item.supply))
        if len(restock) > 0:
            warning = ""
            for name, supply in restock:
                warning += "Warning: %s stock at %d!\n" % (name, supply)
            print warning
            if USE_EMAIL:
                send_mail('Stock warning', warning, 'noztek.inventory@gmail.com',
                        ['info@noztek.com'], fail_silently=True)
                send_mail('Stock warning', warning, 'noztek.inventory@gmail.com',
                        ['nseymoursmith@gmail.com'], fail_silently=True)
    def save(self, *args, **kwargs):
        self.adjustStock()
        super(AdditionalItem, self).save(*args, **kwargs)

    def __unicode__(self):
        return self.item.name

class ItemRequirement(models.Model):
    product = models.ForeignKey(Product)
    item = models.ForeignKey(Item)
    number_required = models.IntegerField(default = 1)
   
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

# #TODO: Can we make it so that if a Stock order is deleted, we can also reduce associated stock?
# #      Maybe more complicated than it needs to be, we could just use breakage
# class StockOrder(models.Model):
#     supplier = models.ForeignKey(Supplier)
#     date = models.DateTimeField('Date Ordered')
#     delivery_date = models.DateField('Delivery Date')
# #    date.auto_now_add
#     items_ordered = models.ManyToManyField(Item, through='ItemOrder')
#     delivered = models.BooleanField('Delivered?', default = False)
#     def save(self, *args, **kwargs):
#         if self.pk:
#             orig = StockOrder.objects.get(pk = self.pk)
#             if orig.delivered != self.delivered:
#                 if self.delivered:
#                     for entry in self.items_ordered.all():
#                         entry.supply += ItemOrder.objects.filter(stock_order__date=self.date).filter(item__name=entry.name)[0].number_ordered
#                         entry.save()
#                 else:
#                     for entry in self.items_ordered.all():
#                         entry.supply -= ItemOrder.objects.filter(stock_order__date=self.date).filter(item__name=entry.name)[0].number_ordered
#                         entry.save()
#         if not self.pk and self.delivered:
#             #TODO CHECK IF THIS REALLY WORKS --> NO SAME BUG AS BELOW
#             super(StockOrder, self).save(*args, **kwargs)
#             for entry in self.items_ordered.all():
#                 entry.supply += ItemOrder.objects.filter(stock_order__date=self.date).filter(item__name=entry.name)[0].number_ordered
#                 entry.save() 
#         super(StockOrder, self).save(*args, **kwargs)

#     def __unicode__(self):
#         return self.supplier.name

# class StockCorrection(models.Model):
#     warning = models.CharField(max_length = 256, default = "Warning: this can only be applied once. Changing values after creation will have no effect - don't do it!")
#     date = models.DateTimeField('Date Ordered')
#     items_adjusted = models.ManyToManyField(Item, through='StockChange')
#     reason = models.CharField(max_length = 256)
#     adjusted = models.BooleanField(default = False)
    
#     def __unicode__(self):
#         return self.reason

# @receiver(post_save, sender=StockCorrection, dispatch_uid="update_stock")
# def update_stock(sender, instance, **kwargs):
#     print "got to the post save"
#     if not instance.adjusted:
#         print "adjusting stock"
#         print StockChange.objects.filter(correction__date = instance.date).filter(correction__reason = instance.reason)
#         print instance.items_adjusted.all()
#         for entry in instance.items_adjusted.all():
#             print "got stuff!"
#             entry.supply += ItemOrder.objects.filter(stock_order__date=self.date).filter(item__name=entry.name)[0].number_changed
#             entry.save()
#         instance.adjusted = True
#         instance.save()



# class ProductOrder(models.Model):
#     customer = models.ForeignKey(Customer)
#     product = models.ForeignKey(Product)
#     number_ordered = models.IntegerField(default = 1)
#     date = models.DateTimeField('Date Ordered')
#     completion_date = models.DateField('Completion Date')
# #    items_used = models.ManyToManyField(Item, through='ItemOrder')
#     completed = models.BooleanField('Completed?', default = False)

#     def adjustStock(self):
#         restock = []
#         if not self.pk and self.completed:
#             for entry in self.product.req_item.all():
#                 entry.supply -= ItemRequirement.objects.filter(product__name=self.product.name).filter(item__name=entry.name)[0].number_required
#                 entry.save()
#                 if entry.supply < entry.minimum:
#                     restock.append((entry.name, entry.supply))
#         if self.pk:
#             orig = ProductOrder.objects.get(pk = self.pk)
#             if orig.completed != self.completed:
#                 if self.completed:
#                     for entry in self.product.req_item.all():
#                         entry.supply -= ItemRequirement.objects.filter(product__name=self.product.name).filter(item__name=entry.name)[0].number_required
#                         entry.save()
#                         if entry.supply < entry.minimum:
#                             restock.append((entry.name, entry.supply))
#                 else:
#                     for entry in self.product.req_item.all():
#                         entry.supply += ItemRequirement.objects.filter(product__name=self.product.name).filter(item__name=entry.name)[0].number_required
#                         entry.save()
#                         if entry.supply < entry.minimum:
#                             restock.append((entry.name, entry.supply))
#         if len(restock) > 0:
#             warning = ""
#             for name, supply in restock:
#                 warning += "Warning: %s stock at %d!\n" % (name, supply)
#             print warning
#             if USE_EMAIL:
#                 send_mail('Stock warning', warning, 'noztek.inventory@gmail.com',
#                         ['info@noztek.com'], fail_silently=True)
#                 send_mail('Stock warning', warning, 'noztek.inventory@gmail.com',
#                         ['nseymoursmith@gmail.com'], fail_silently=True)

#     def save(self, *args, **kwargs):
#         self.adjustStock()
#         super(ProductOrder, self).save(*args, **kwargs)

#     def __unicode__(self):
#         return self.product.name

# class ItemOrder(models.Model):
#     stock_order = models.ForeignKey(StockOrder)
#     item = models.ForeignKey(Item)
#     number_ordered = models.IntegerField(default = 0)

#     def number_stocked(self):
#         if self.item == None: return "undefined"
#         return self.item.supply

#     def __unicode__(self):
#         return self.stock_order.supplier.name

# class StockChange(models.Model):
#     correction = models.ForeignKey(StockCorrection)
#     item = models.ForeignKey(Item)
#     number_changed = models.IntegerField(default = 0)

#     def number_stocked(self):
#         if self.item == None: return "undefined"
#         return self.item.supply

#     def __unicode__(self):
#         return self.correction.reason
