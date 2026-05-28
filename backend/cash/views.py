from django.shortcuts import render
from rest_framework.exceptions import ValidationError
from rest_framework import viewsets, permissions
from .models import Cash
from .serializers import CashSerializer, CashOpeningSerializer
from django.db.models import Q, Sum
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Cash, CashOpening
from decimal import Decimal
from sales.models import Venta
from django.db import models 

        

timezone = __import__('django.utils.timezone').utils.timezone

class CashViewSet(viewsets.ModelViewSet):
    serializer_class = CashSerializer
    permission_classes = [permissions.IsAuthenticated]
    

    def get_queryset(self):
        user = self.request.user
        if not user.roles.filter(rolNom__in=["GERENTE", "SUPERVISOR", "VENDEDOR","CAJERO"]).exists():
            return Cash.objects.none()

        if user.roles.filter(rolNom="GERENTE").exists():
            return Cash.objects.all()

        # Si es CAJERO, VENDEDOR o SUPERVISOR, mostrar solo sus cajas asignadas
        return Cash.objects.filter(usuCod=user)
    
    def perform_create(self, serializer):
        serializer.save()


class CashOpeningViewSet(viewsets.ModelViewSet):
    serializer_class = CashOpeningSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user

        if user.roles.filter(rolNom="CAJERO").exists():
            return CashOpening.objects.filter(usuCod=user)

        return CashOpening.objects.all()
    
    @action(detail=False, methods=['get'], url_path='by-cash/(?P<cajCod>[^/.]+)')
    def aperturas_por_caja(self, request, cajCod=None):
        user = request.user

        if user.roles.filter(rolNom="CAJERO").exists():
            aperturas = CashOpening.objects.filter(usuCod=user, cajCod=cajCod)
        else:
            aperturas = CashOpening.objects.filter(cajCod=cajCod)

        serializer = self.get_serializer(aperturas, many=True)
        return Response(serializer.data)

    def perform_create(self, serializer):
        user = self.request.user
        caja = serializer.validated_data['cajCod']

        # Validar que el cajero solo abra su caja asignada
        if user.roles.filter(rolNom="CAJERO").exists():
            if caja.usuCod != user:
                raise ValidationError("No puedes abrir una caja que no te fue asignada.")
        
        # NUEVO: Verificar que no haya otra apertura abierta para esta caja
        apertura_existente = CashOpening.objects.filter(
            cajCod=caja,
            cajaAperEstado="ABIERTA"
        ).exists()
        
        if apertura_existente:
            raise ValidationError(f"La caja {caja.cajNom} ya tiene una apertura abierta. Ciérrala antes de abrir una nueva.")
        
        #  NUEVO: Verificar que el usuario no tenga otra apertura abierta
        apertura_usuario = CashOpening.objects.filter(
            usuCod=user,
            cajaAperEstado="ABIERTA"
        ).exists()
        
        if apertura_usuario:
            raise ValidationError("Ya tienes una apertura abierta. Ciérrala antes de abrir otra.")
        
        serializer.save(usuCod=user)
    
    def perform_close(self, apertura, user, monto_cierre, observaciones=""):
        """Cierra una apertura de caja"""
        #  CORREGIDO: Solo validar para CAJEROS, otros roles pueden cerrar cualquier caja
        if user.roles.filter(rolNom="CAJERO").exists():
            if apertura.usuCod != user:
                raise ValidationError("No puedes cerrar una apertura que no te pertenece.")

        if apertura.cajaAperEstado != "ABIERTA":
            raise ValidationError("La caja ya está cerrada.")

        # ✅ CORREGIDO: Calcular el monto esperado dinámicamente
        from sales.models import Venta
        ventas_total = Venta.objects.filter(
            cajaAperCod=apertura,
            ventAnulada=False
        ).aggregate(total=models.Sum('ventTotal'))['total'] or Decimal('0')
        
        esperado = apertura.cajaAperMontInicial + ventas_total
        diferencia = Decimal(str(monto_cierre)) - esperado

        apertura.cajaAperMontCierre = Decimal(str(monto_cierre))
        apertura.cajaAperMontEsperado = esperado
        apertura.cajaAperDiferencia = diferencia
        apertura.cajaAperFechaHorCierre = timezone.now()
        apertura.cajaAperEstado = "CERRADA"
        apertura.cajaAperObservacio = observaciones
        apertura.save()
        
        print(f"✓ Caja cerrada: Esperado={esperado}, Cierre={monto_cierre}, Diferencia={diferencia}")

    @action(detail=False, methods=['post'], url_path='close')
    def cerrar_caja(self, request):
        """Cierra la caja abierta del usuario actual"""
        user = request.user
        
        # Buscar apertura abierta según el rol
        if user.roles.filter(rolNom="CAJERO").exists():
            apertura = CashOpening.objects.filter(
                usuCod=user, 
                cajaAperEstado="ABIERTA"
            ).first()
        else:
            apertura = CashOpening.objects.filter(
                cajaAperEstado="ABIERTA"
            ).first()

        if not apertura:
            return Response(
                {"detail": "No hay caja abierta para cerrar."}, 
                status=404
            )
        
        # Obtener datos del request
        monto_cierre = request.data.get("cajaAperMontCierre")
        observaciones = request.data.get("cajaAperObservacio", "")
        
        if monto_cierre is None:
            return Response(
                {"detail": "Debes enviar el monto de cierre."}, 
                status=400
            )

        try:
            #  Pasar las observaciones al método perform_close
            self.perform_close(apertura, user, monto_cierre, observaciones)
        except ValidationError as e:
            return Response(
                {"detail": str(e.detail)}, 
                status=400
            )

        return Response(
            {"detail": "Caja cerrada correctamente."}, 
            status=200
        )
    
    @action(detail=False, methods=['get'], url_path='open')
    def abrir_actual(self, request):
        """
        Devuelve la apertura ABIERTA actual para el usuario (si es CAJERO)
        o para la sucursal del usuario (GERENTE/SUPERVISOR).
        Retorna null (200) si no hay apertura abierta.
        """
        user = request.user

        if user.roles.filter(rolNom="CAJERO").exists():
            apertura = CashOpening.objects.filter(
                usuCod=user, 
                cajaAperEstado="ABIERTA"
            ).order_by('-cajaApertuFechHora').first()
        else:
            apertura = CashOpening.objects.filter(
                cajaAperEstado="ABIERTA"
            ).order_by('-cajaApertuFechHora').first()

        if not apertura:
            return Response(None, status=200)

        serializer = self.get_serializer(apertura)
        return Response(serializer.data)


    @action(detail=False, methods=['get'])
    def session_sales(self, request):
        """Obtener resumen de ventas de la sesión actual"""
        user = request.user
        
        # Buscar apertura abierta según el rol (igual que en abrir_actual)
        if user.roles.filter(rolNom="CAJERO").exists():
            apertura = CashOpening.objects.filter(
                usuCod=user, 
                cajaAperEstado="ABIERTA"
            ).first()
        else:
            apertura = CashOpening.objects.filter(
                cajaAperEstado="ABIERTA"
            ).first()
        
        if not apertura:
            return Response({'error': 'No hay caja abierta'}, status=400)
        

        # Obtener ventas de esta sesión (relacionadas con esta apertura)
        ventas = Venta.objects.filter(
            cajaAperCod=apertura,
            ventAnulada=False
        )
        
        # Calcular totales por forma de pago
        ventas_por_forma = {
            'EFECTIVO': Decimal('0.00'),
            'TARJETA': Decimal('0.00'),
            'TRANSFERENCIA': Decimal('0.00'),
            'YAPE': Decimal('0.00'),
            'PLIN': Decimal('0.00'),
            'MIXTO': Decimal('0.00'),
        }
        
        total_ventas = Decimal('0.00')
        
        for venta in ventas:
            forma = venta.ventFormaPago
            monto = Decimal(str(venta.ventTotal))
            total_ventas += monto
            
            if forma in ventas_por_forma:
                ventas_por_forma[forma] += monto
        
        return Response({
            'total_ventas': float(total_ventas),
            'cantidad_ventas': ventas.count(),
            'ventas_por_forma_pago': {k: float(v) for k, v in ventas_por_forma.items()}
        })