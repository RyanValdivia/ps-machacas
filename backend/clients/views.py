from django.shortcuts import render
# viwesets con la mejor practica client optometra y receta, creacion de Client edicion y eliminacion y para agregarle una receta a mas
from rest_framework import viewsets, status
from rest_framework.response import Response
from .models import Client, Optometrist, Recipe
from .serializers import ClientSerializer, OptometristSerializer, RecipeSerializer
from rest_framework.pagination import PageNumberPagination
from rest_framework import filters
from django_filters.rest_framework import DjangoFilterBackend
from .filters import ClientFilter
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated


class ClientPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 50

class ClientViewSet(viewsets.ModelViewSet):
    queryset = Client.objects.all().order_by('cliNomCompleto')
    serializer_class = ClientSerializer
    pagination_class = ClientPagination

    filter_backends = [
        filters.SearchFilter,
        DjangoFilterBackend
    ]

    search_fields = ['cliNomCompleto', 'cliNumDoc']
    filterset_class = ClientFilter

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'success': True, 'data': serializer.data}, status=status.HTTP_201_CREATED)
        return Response({'success': False, 'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        if serializer.is_valid():
            serializer.save()
            return Response({'success': True, 'data': serializer.data})
        return Response({'success': False, 'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def list(self, request, *args, **kwargs):
        # Filtramos (Búsqueda)
        queryset = self.filter_queryset(self.get_queryset())
        
        # Paginamos
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        # Si hay paginación, devolvemos todo
        serializer = self.get_serializer(queryset, many=True)
        return Response({'success': True, 'data': serializer.data})

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def buscar_cliente_por_documento(request):
    """
    Busca un cliente por tipo y número de documento
    GET /api/clients/buscar/?tipo=DNI&numero=12345678
    """
    tipo_doc = request.query_params.get('tipo', 'DNI')
    num_doc = request.query_params.get('numero', '')
    
    if not num_doc:
        return Response(
            {'error': 'Número de documento requerido'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        cliente = Client.objects.get(
            cliTipoDoc=tipo_doc,
            cliNumDoc=num_doc
        )
        serializer = ClientSerializer(cliente)
        return Response({
            'encontrado': True,
            'cliente': serializer.data
        }, status=status.HTTP_200_OK)
    
    except Client.DoesNotExist:
        return Response(
            {
                'encontrado': False,
                'mensaje': 'Cliente no encontrado en base de datos'
            },
            status=status.HTTP_200_OK  # ← Nota: 200 OK, no 404
        )
    except Client.MultipleObjectsReturned:
        # Por si acaso hay duplicados
        return Response(
            {'error': 'Se encontraron múltiples clientes con ese documento'},
            status=status.HTTP_400_BAD_REQUEST
        )


class OptometristViewSet(viewsets.ModelViewSet):
    # Definimos el queryset base y el ordenamiento
    queryset = Optometrist.objects.all().order_by('optNombre', 'optApellido')
    serializer_class = OptometristSerializer
    
    # Habilitamos campos de búsqueda para que el frontend (?search=juan) funcione
    search_fields = ['optNombre', 'optApellido'] 

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'success': True, 'data': serializer.data}, status=status.HTTP_201_CREATED)
        return Response({'success': False, 'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        if serializer.is_valid():
            serializer.save()
            return Response({'success': True, 'data': serializer.data})
        return Response({'success': False, 'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def list(self, request, *args, **kwargs):
        # Filtramos (Búsqueda)
        queryset = self.filter_queryset(self.get_queryset())
        
        # Paginamos
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        # Si no hay paginación, devolvemos todo
        serializer = self.get_serializer(queryset, many=True)
        return Response({'success': True, 'data': serializer.data})

class RecipeViewSet(viewsets.ModelViewSet):
    # Definimos el queryset base y el ordenamiento
    queryset = Recipe.objects.all().order_by('-recFech')
    serializer_class = RecipeSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ['cliCod']   
    # Habilitamos campos de búsqueda para que el frontend (?search=juan) funcione
    search_fields = ['recFech', 'recEstado', 'recObservaciones', 'recInfoExtra', 'receDIP', 'receDIPCerca', 'receAdd', 'receEsfeOD', 'receCilinOD', 'receEjeOD', 'receAvccOD', 'receEsfeOI', 'receCilinOI', 'receEjeOI', 'receAvccOI', 'receEsExterna', 'diagnostico', 'cliCod__cliNomCompleto', 'cliCod__cliNumDoc', 'receOptometra__optNombre', 'receOptometra__optApellido'] 

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'success': True, 'data': serializer.data}, status=status.HTTP_201_CREATED)
        return Response({'success': False, 'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        if serializer.is_valid():
            serializer.save()
            return Response({'success': True, 'data': serializer.data})
        return Response({'success': False, 'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def list(self, request, *args, **kwargs):
        # Filtramos (Búsqueda)
        queryset = self.filter_queryset(self.get_queryset())
        print("QUERY PARAMS:", request.query_params)
        # Paginamos
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        # Si no hay paginación, devolvemos todo
        serializer = self.get_serializer(queryset, many=True)
        return Response({'success': True, 'data': serializer.data})
