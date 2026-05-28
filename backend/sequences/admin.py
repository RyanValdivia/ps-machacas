from django.contrib import admin
from .models import ProductSequence

@admin.register(ProductSequence)
class ProductSequenceAdmin(admin.ModelAdmin):
    list_display = ('sequence_type', 'current_value', 'description', 'updated_at')
    list_filter = ('sequence_type',)
    search_fields = ('sequence_type', 'description')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Informacion Principal', {
            'fields': ('sequence_type', 'current_value', 'description')
        }),
        ('Auditoria', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def has_delete_permission(self, request, obj=None):
        # Prevenir eliminacion accidental de secuencias
        return request.user.is_superuser