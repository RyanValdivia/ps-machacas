from rest_framework import serializers
from .models import Client, Optometrist, Recipe

class ClientSerializer(serializers.ModelSerializer):
    cliCod = serializers.IntegerField(read_only=True)
    cliTipoDoc = serializers.CharField(required=False, allow_blank=True)
    cliNumDoc = serializers.CharField(required=False, allow_blank=True)
    cliNomCompleto = serializers.CharField()  # Obligatorio
    cliTelef = serializers.CharField(required=False, allow_blank=True)
    cliFechaNac = serializers.DateField(required=False, allow_null=True)

    class Meta:
        model = Client
        fields = [
            'cliCod', 'cliTipoDoc', 'cliNumDoc', 'cliNomCompleto',
            'cliTelef', 'cliFechaNac'
        ]


class OptometristSerializer(serializers.ModelSerializer):
    class Meta:
        model = Optometrist
        fields = ['optCod', 'optNombre', 'optApellido']


class RecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = [
            'recCod', 'recFech', 'recEstado', 'recObservaciones', 'recInfoExtra',
            'receDIP', 'receDIPCerca', 'receAdd', 'receEsfeOD', 'receCilinOD', 'receEjeOD',
            'receAvccOD', 'receEsfeOI', 'receCilinOI', 'receEjeOI', 'receAvccOI', 'receEsExterna', 
            'diagnostico', 'cliCod', 'optCod'
        ]
        extra_kwargs = {
            'recEstado': {'required': False},
            'recObservaciones': {'required': False},
            'recInfoExtra': {'required': False},
            'receDIP': {'required': False},
            'receDIPCerca': {'required': False},
            'receAdd': {'required': False},
            'receEsfeOD': {'required': False},
            'receCilinOD': {'required': False},
            'receEjeOD': {'required': False},
            'receAvccOD': {'required': False},
            'receEsfeOI': {'required': False},
            'receCilinOI': {'required': False},
            'receEjeOI': {'required': False},
            'receAvccOI': {'required': False},
            'receEsExterna': {'required': False},
            'diagnostico': {'required': False},
        }
