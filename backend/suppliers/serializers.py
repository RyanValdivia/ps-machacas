from rest_framework import serializers
from .models import Supplier
import re

class SupplierSerializer(serializers.ModelSerializer):
    class Meta:
        model = Supplier
        fields =[
            'provCod',
            'provRuc',
            'provRazSocial',
            'provDirec',
            'provTele',
            'provEmail',
            'provCiu',
            'provEstado',

        ]
        read_only_fields = ['provCod']
        extra_kwargs = {
            'provRuc': {'required': False, 'allow_blank': True, 'allow_null': True},
            'provDirec': {'required': False, 'allow_blank': True, 'allow_null': True},
            'provTele': {'required': False, 'allow_blank': True, 'allow_null': True},
            'provEmail': {'required': False, 'allow_blank': True, 'allow_null': True},
            'provCiu': {'required': False, 'allow_blank': True, 'allow_null': True},
        }
    
    def to_internal_value(self, data):
        # Convertir cadenas vacías a None antes de la validación
        for field in ['provRuc', 'provDirec', 'provTele', 'provEmail', 'provCiu']:
            if field in data and (data[field] == '' or data[field] is None or (isinstance(data[field], str) and data[field].strip() == '')):
                data[field] = None
        return super().to_internal_value(data)

    def validate_provRuc(self, value):
        # Si no se proporciona valor, retornar None
        if value is None or (isinstance(value, str) and value.strip() == ''):
            return None
            
        value = value.strip()
        
        # Comprobar si tiene exactamente 11 dígitos
        if not re.match(r'^\d{11}$', value):
            raise serializers.ValidationError(
                "El RUC debe tener exactamente 11 dígitos numéricos"
            )
        
        # Verificar unicidad al crear
        if not self.instance:
            if Supplier.objects.filter(provRuc=value).exists():
                raise serializers.ValidationError(
                    "Ya existe un proveedor con este RUC"
                )
        # Verificar unicidad en la actualización
        else:
            if Supplier.objects.filter(provRuc=value).exclude(
                provCod=self.instance.provCod
            ).exists():
                raise serializers.ValidationError(
                    "Ya existe un proveedor con este RUC"
                )
        
        return value
    
    def validate_provTele(self, value):
        # Si no se proporciona valor, retornar None
        if value is None or (isinstance(value, str) and value.strip() == ''):
            return None
            
        value = value.strip()
        
        # Comprobar si tiene exactamente 9 dígitos
        if not re.match(r'^\d{9}$', value):
            raise serializers.ValidationError(
                "El número de teléfono debe tener exactamente 9 dígitos numéricos"
            )
        
        return value
    
    def validate_provRazSocial(self, value):
        value = ' '.join(value.split())
        #corregir la longitud del minimo
        if len(value) < 3:
            raise serializers.ValidationError(
                "Business name must be at least 3 characters long"
            )
        
        if len(value) > 255:
            raise serializers.ValidationError(
                "Business name cannot exceed 255 characters"
            )
        
        return value
    
    def validate_provEmail(self, value):
        # Si no se proporciona valor, retornar None
        if value is None or (isinstance(value, str) and value.strip() == ''):
            return None
            
        value = value.strip().lower()
        
        # Validación básica de expresiones regulares para correo electrónico
        email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_regex, value):
            raise serializers.ValidationError(
                "Ingrese una dirección de correo electrónico válida"
            )
        
        return value
    
    def validate_provDirec(self, value):
        # Si no se proporciona valor, retornar None
        if value is None or (isinstance(value, str) and value.strip() == ''):
            return None
            
        value = value.strip()
        
        # Solo validar longitud si se proporciona un valor
        if len(value) < 5:
            raise serializers.ValidationError(
                "La dirección debe tener al menos 5 caracteres"
            )
        
        return value
    
    def validate_provCiu(self, value):
        # Si no se proporciona valor, retornar None
        if value is None or (isinstance(value, str) and value.strip() == ''):
            return None
            
        value = value.strip()
        
        # Solo validar longitud si se proporciona un valor
        if len(value) < 2:
            raise serializers.ValidationError(
                "El nombre de la ciudad debe tener al menos 2 caracteres"
            )
        
        return value
    
    def validate_provEstado(self, value):
        valid_statuses = ['Active', 'Inactive']
        if value not in valid_statuses:
            raise serializers.ValidationError(
                f"El estado debe ser uno de los siguientes: {', '.join(valid_statuses)}"
            )
        
        return value
    

class SupplierListSerializer(serializers.ModelSerializer):
    #Serializador simplificado para listar proveedores
    class Meta:
        model = Supplier
        fields = [
            'provCod',
            'provRuc',
            'provRazSocial',
            'provDirec',
            'provTele',
            'provEmail',
            'provCiu',
            'provEstado',
        ]