from rest_framework import serializers
from .models import OpticalCenter
from django.conf import settings
import os
import base64

class OpticalCenterSerializer(serializers.ModelSerializer):
    optCod = serializers.IntegerField(source='id', read_only=True)
    optLogo = serializers.ImageField(required=False, allow_null=True, write_only=True)
    optLogoUrl = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = OpticalCenter
        fields = ['id', 'optCod', 'optNom', 'optLema', 'optDir', 'optProv', 'optTel', 'optLogo', 'optLogoUrl']
        read_only_fields = ('id', 'optCod', 'optLogoUrl')
    
    def get_optLogoUrl(self, obj):
        """Devolver la imagen como base64 data URL para compatibilidad con Tauri"""
        if not obj.optLogo:
            return None
        
        try:
            # Leer el archivo de imagen
            with open(obj.optLogo.path, 'rb') as image_file:
                image_data = image_file.read()
                
            # Detectar el tipo MIME
            file_extension = obj.optLogo.name.split('.')[-1].lower()
            mime_types = {
                'jpg': 'image/jpeg',
                'jpeg': 'image/jpeg',
                'png': 'image/png',
                'gif': 'image/gif',
                'webp': 'image/webp'
            }
            mime_type = mime_types.get(file_extension, 'image/jpeg')
            
            # Convertir a base64
            base64_data = base64.b64encode(image_data).decode('utf-8')
            
            # Devolver como data URL
            data_url = f"data:{mime_type};base64,{base64_data}"
            print(f"🖼️ [SERIALIZER] Logo convertido a base64 (primeros 100 chars): {data_url[:100]}...")
            
            return data_url
            
        except Exception as e:
            print(f"❌ [SERIALIZER] Error al convertir logo a base64: {e}")
            return None
    
    def to_representation(self, instance):
        """Personalizar la representación"""
        representation = super().to_representation(instance)
        # Eliminar el campo optLogo de la respuesta (es write_only)
        # optLogoUrl ya contiene la imagen en base64
        return representation
    
    def update(self, instance, validated_data):
        """Manejar la actualización del logo correctamente"""
        print(f"📝 [SERIALIZER] Actualizando OpticalCenter con datos: {validated_data.keys()}")
        
        # Si viene un nuevo logo
        if 'optLogo' in validated_data:
            new_logo = validated_data.get('optLogo')
            
            if new_logo:
                print(f"📸 [SERIALIZER] Nuevo logo recibido: {new_logo.name}, tamaño: {new_logo.size} bytes")
                
                # Eliminar logo anterior si existe
                if instance.optLogo:
                    old_logo_path = instance.optLogo.path
                    if os.path.exists(old_logo_path):
                        try:
                            os.remove(old_logo_path)
                            print(f"🗑️ [SERIALIZER] Logo anterior eliminado: {old_logo_path}")
                        except Exception as e:
                            print(f"⚠️ [SERIALIZER] No se pudo eliminar logo anterior: {e}")
                
                instance.optLogo = new_logo
            elif new_logo is None:
                # Si se envió None, eliminar el logo
                if instance.optLogo:
                    try:
                        os.remove(instance.optLogo.path)
                        print(f"🗑️ [SERIALIZER] Logo eliminado")
                    except:
                        pass
                instance.optLogo = None
        
        # Actualizar otros campos
        for attr, value in validated_data.items():
            if attr != 'optLogo':
                setattr(instance, attr, value)
        
        instance.save()
        print(f"✅ [SERIALIZER] OpticalCenter actualizado exitosamente")
        return instance