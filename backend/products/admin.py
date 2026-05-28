from django.contrib import admin
from .models import Product

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('prodCode', 'prodDescr', 'catproCod', 'prodStock', 'prodCostoInv', 'prodPrecioVenta')
    list_filter = ('catproCod', 'prodEstado', 'prodMate')
    search_fields = ('prodCode', 'prodMarca', 'prodDescr')
    readonly_fields = ('prodCode', 'prodDescr', 'created_at', 'updated_at')
    
    fieldsets = (
        ('Categoria y Proveedor', {
            'fields': ('catproCod', 'provCod', 'prodEstado')
        }),
        ('Detalles - Monturas', {
            'fields': ('prodMarca', 'prodMate', 'prodTalla', 'prodColor', 'prodGenero'),
            'description': 'Marca y Talla son obligatorios para monturas. Material define el codigo.'
        }),
        ('Precios e Inventario', {
            'fields': ('prodCostoInv', 'prodPrecioVenta', 'prodStock', 'prodStockMin')
        }),
        ('Informacion Automatica', {
            'fields': ('prodCode', 'prodDescr', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )