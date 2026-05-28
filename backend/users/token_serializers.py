from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework import serializers
from django.contrib.auth import authenticate

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    # Cambiar nombres de campos para que coincidan con tu modelo
    username_field = 'usuNom'  # En lugar de 'username'
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Reemplazar el campo 'username' por 'usuNom'
        self.fields[self.username_field] = serializers.CharField()
        self.fields['usuContra'] = serializers.CharField(write_only=True)
        # Eliminar campos por defecto de JWT
        self.fields.pop('username', None)
        self.fields.pop('password', None)
    
    def validate(self, attrs):
        # Obtener credenciales con los nombres correctos
        usuNom = attrs.get('usuNom')
        usuContra = attrs.get('usuContra')
        
        if usuNom and usuContra:
            # Autenticar usando Django authenticate
            user = authenticate(
                request=self.context.get('request'),
                username=usuNom,  # Django authenticate usa 'username' internamente
                password=usuContra
            )
            
            if not user:
                raise serializers.ValidationError(
                    {'detail': 'Credenciales inválidas. Verifica tu usuario y contraseña.'},
                    code='authorization'
                )
            
            if not user.is_active:
                raise serializers.ValidationError(
                    {'detail': 'Esta cuenta está desactivada.'},
                    code='authorization'
                )
        else:
            raise serializers.ValidationError(
                {'detail': 'Debe proporcionar "usuNom" y "usuContra".'},
                code='authorization'
            )
        
        # Generar tokens usando el usuario autenticado
        refresh = self.get_token(user)
        
        data = {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }
        
        # Opcional: agregar información adicional del usuario
        data['user'] = {
            'usuCod': user.usuCod,
            'usuNom': user.usuNom,
            'usuEmail': user.usuEmail,
            'usuNombreCom': user.usuNombreCom,
        }
        
        return data
    
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        
        # Agregar claims personalizados al token
        token['usuNom'] = user.usuNom
        token['usuEmail'] = user.usuEmail
        token['usuCod'] = user.usuCod
        
        return token


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer
