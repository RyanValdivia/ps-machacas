from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
import requests
import os

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def consultar_dni(request):
    """
    Proxy para consultar DNI en APIs externas
    GET /api/proxy/dni?numero=12345678
    """
    numero = request.GET.get('numero', '')
    
    if not numero:
        return Response(
            {'error': 'Debe proporcionar el número de DNI'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Validar que sea un DNI de 8 dígitos
    if not numero.isdigit() or len(numero) != 8:
        return Response(
            {'error': 'DNI inválido. Debe tener 8 dígitos.'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        # Intentar con APIs.net.pe (API pública gratuita v1)
        api_url = f"https://api.apis.net.pe/v1/dni?numero={numero}"
        
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }
        
        response = requests.get(
            api_url,
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            return Response(data, status=status.HTTP_200_OK)
        elif response.status_code == 404:
            return Response(
                {'error': 'DNI no encontrado en la base de datos de RENIEC'},
                status=status.HTTP_404_NOT_FOUND
            )
        elif response.status_code == 429:
            return Response(
                {'error': 'Límite de consultas alcanzado. Intente más tarde.'},
                status=status.HTTP_429_TOO_MANY_REQUESTS
            )
        else:
            return Response(
                {'error': f'Error al consultar DNI: {response.status_code}'},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )
            
    except requests.exceptions.Timeout:
        return Response(
            {'error': 'Tiempo de espera agotado al consultar DNI'},
            status=status.HTTP_504_GATEWAY_TIMEOUT
        )
    except requests.exceptions.ConnectionError:
        return Response(
            {'error': 'Error de conexión con el servicio de RENIEC'},
            status=status.HTTP_503_SERVICE_UNAVAILABLE
        )
    except Exception as e:
        return Response(
            {'error': f'Error inesperado: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def consultar_ruc(request):
    """
    Proxy para consultar RUC en SUNAT
    GET /api/proxy/ruc?numero=20123456789
    """
    numero = request.GET.get('numero', '')
    
    if not numero:
        return Response(
            {'error': 'Debe proporcionar el número de RUC'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Validar que sea un RUC de 11 dígitos
    if not numero.isdigit() or len(numero) != 11:
        return Response(
            {'error': 'RUC inválido. Debe tener 11 dígitos.'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        # Intentar con APIs.net.pe v1 (API pública gratuita)
        api_url = f"https://api.apis.net.pe/v1/ruc?numero={numero}"
        
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }
        
        response = requests.get(
            api_url,
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            return Response(data, status=status.HTTP_200_OK)
        elif response.status_code == 404:
            return Response(
                {'error': 'RUC no encontrado en SUNAT'},
                status=status.HTTP_404_NOT_FOUND
            )
        elif response.status_code == 429:
            return Response(
                {'error': 'Límite de consultas alcanzado. Intente más tarde.'},
                status=status.HTTP_429_TOO_MANY_REQUESTS
            )
        else:
            return Response(
                {'error': f'Error al consultar RUC: {response.status_code}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
            
    except requests.exceptions.Timeout:
        return Response(
            {'error': 'Tiempo de espera agotado al consultar RUC'},
            status=status.HTTP_504_GATEWAY_TIMEOUT
        )
    except requests.exceptions.ConnectionError:
        return Response(
            {'error': 'Error de conexión con el servicio de SUNAT'},
            status=status.HTTP_503_SERVICE_UNAVAILABLE
        )
    except Exception as e:
        return Response(
            {'error': f'Error inesperado: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
