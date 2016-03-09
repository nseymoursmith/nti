from django.contrib import admin

from django import forms

from .models import Location

from .models import Item

from .models import ItemLocation

from .models import Supplier

from .models import ItemSupplier

from .models import Product

from .models import ItemRequirement

from .models import StockOrder

from .models import ItemOrder

from .models import ProductOrder

from .models import Customer

from .models import StockCorrection

from .models import StockChange

#from .models import Event
#from .models import EventStock

class ItemLocationInline(admin.TabularInline):
    model = ItemLocation
    extra = 0

class ItemSupplierInline(admin.TabularInline):
    model = ItemSupplier
    extra = 0

class ItemOrderInline(admin.TabularInline):
    model = ItemOrder
    readonly_fields = ('stock_report',)
    def stock_report(self, instance):
        return instance.number_stocked()
    stock_report.short_description = "In Stock: "
    extra = 0

class StockChangeInline(admin.TabularInline):
    model = StockChange
    readonly_fields = ('stock_report',)
    def stock_report(self, instance):
        return instance.number_stocked()
    stock_report.short_description = "In Stock: "
    extra = 0

class ItemRequirementInline(admin.TabularInline):
    model = ItemRequirement
    readonly_fields = ('stock_report',)
    def stock_report(self, instance):
        return instance.number_stocked()
    stock_report.short_description = "In Stock: "
    extra = 0

# class ItemRequirementAdmin(admin.ModelAdmin):
#     readonly_fields = ('stock_report',)
#     def stock_report(self, instance):
#         return instance.number_stocked()
#     stock_report.short_description = "In Stock: "

class ItemAdmin(admin.ModelAdmin):
    inlines = [ItemLocationInline, ItemSupplierInline]
    list_display = ('name','supply')

class CustomerAdmin(admin.ModelAdmin):
    list_display = ('name','email', 'phone')

class SupplierAdmin(admin.ModelAdmin):
    list_display = ('name','website', 'email', 'phone')

class ProductAdmin(admin.ModelAdmin):
    inlines = [ItemRequirementInline]
    save_as = True

class StockOrderAdmin(admin.ModelAdmin):
    inlines = [ItemOrderInline]
    list_display = ('supplier', 'date', 'delivery_date', 'delivered')
    save_as = True

class ProductOrderAdmin(admin.ModelAdmin):
    list_display = ('product', 'number_ordered', 'customer', 'date', 'completion_date', 'completed')
    save_as = True

class StockCorrectionAdmin(admin.ModelAdmin):
    inlines = [StockChangeInline]
    list_display = ('date', 'reason')
    readonly_fields = ("warning",)
    # def get_readonly_fields(self, request, obj=None):
    #     if obj: # editing an existing object
    #         return self.readonly_fields + ('items_changed__number_changed',)
    #     return self.readonly_fields


admin.site.register(Product, ProductAdmin)

#admin.site.register(Location)

#admin.site.register(Supplier)

admin.site.register(Item, ItemAdmin)

admin.site.register(Customer, CustomerAdmin)

admin.site.register(Supplier, SupplierAdmin)

admin.site.register(StockOrder, StockOrderAdmin)

admin.site.register(StockCorrection, StockCorrectionAdmin)

admin.site.register(ProductOrder, ProductOrderAdmin)

#admin.site.register(ItemRequirement, ItemRequirementAdmin)

#admin.site.register(Event, EventAdmin)

#admin.site.register(Ownership)

#admin.site.register(ItemLocation)

#admin.site.register(ItemSupplier)
