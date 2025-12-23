from .models import *
from Products.models import *
from django.contrib import admin
from unfold.admin import ModelAdmin
# Register your models here.

admin.site.register(FAQ,ModelAdmin)
admin.site.register(News,ModelAdmin)
admin.site.register(FootScan,ModelAdmin)
@admin.register(Finance)
class FinanceAdmin(ModelAdmin):
    list_display = ('partner','balance','month','year')
    list_filter = ('partner','month','year')
    search_fields = ('partner__email','balance')
    readonly_fields = ('partner','balance','month','year','this_month_revenue','next_payout','created_at','updated_at')

@admin.register(Payment)
class PaymentAdmin(ModelAdmin):
    list_display = ('payment_from','payment_to','order__order_id','transaction_id','created_at')
    list_filter = ('payment_from','payment_to','created_at')
    search_fields = ('payment_from__email','payment_to__email','transaction_id')
    readonly_fields = ('product','amount','quantity','payment_from','payment_to','order','net_amount','transaction_id','created_at')

@admin.register(Warehouse)
class WarehouseAdmin(ModelAdmin):
    list_display = ('name','partner')
    list_filter = ('partner',)
    search_fields = ('name','partner')

@admin.register(OrderInvoice)
class OrderInvoiceAdmin(ModelAdmin):
    list_display = ('user__email','partner__email','amount', 'created_date')
    list_filter = ('created_date','partner__email','user__email')
    search_fields = ('user__email','partner__email','orders__order_id')
    readonly_fields = ('user','partner','orders','payments','amount','invoice_url','created_date')
    
@admin.register(Order)
class OrderAdmin(ModelAdmin):
    list_display = ('order_id','user__email', 'created_at')
    list_filter = ('created_at','user__email')
    search_fields = ('user__email','order_id')
    readonly_fields = ('user','order_id','name','partner','price','product','size','color','quantity','status','net_amount','tracking','created_at')

    

