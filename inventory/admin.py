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

class ProductAdmin(admin.ModelAdmin):
    inlines = [ItemRequirementInline]
    list_display = ('name', 'supply', 'to_make')

class StockOrderAdmin(admin.ModelAdmin):
    inlines = [ItemOrderInline]
    list_display = ('supplier', 'date', 'delivery_date', 'delivered')

class ProductOrderAdmin(admin.ModelAdmin):
    list_display = ('product', 'date', 'completion_date', 'completed')


admin.site.register(Product, ProductAdmin)

#admin.site.register(Location)

#admin.site.register(Supplier)

admin.site.register(Item, ItemAdmin)

admin.site.register(StockOrder, StockOrderAdmin)

admin.site.register(ProductOrder, ProductOrderAdmin)
#admin.site.register(ItemRequirement, ItemRequirementAdmin)

#admin.site.register(Event, EventAdmin)

#admin.site.register(Ownership)

#admin.site.register(ItemLocation)


#admin.site.register(ItemSupplier)

#BUG when adding a new supplier from stock order admin:
#AFter saving you don't go back to stock order admin,
#but rather get stuck in a window saying 'popup closing'
