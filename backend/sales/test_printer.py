import pytest
from unittest.mock import patch, MagicMock
from decimal import Decimal


# Tests de ImpresoraTermica (sales/printer.py): generación del ticket ESC/POS para
# la impresora térmica de 80mm. Cubre _generar_ticket con distintas combinaciones de
# datos (mínimos, completos, descuento, adelanto parcial/completo, observaciones,
# productos multilínea para lunas), el logo (con/sin OpticalCenter en BD, conversión
# de imagen a ESC/POS), el envío a la impresora vía subprocess (mockeado) y el manejo
# de errores en imprimir_ticket_venta. Cada test ya trae su propio comentario "# TEST:"
# inline describiendo el caso puntual.

@pytest.fixture
def printer():
    from sales.printer import ImpresoraTermica
    return ImpresoraTermica(nombre_impresora="TEST_PRINTER")


@pytest.mark.django_db
class TestImpresoraTermica:
    # TEST: init con nombre por defecto
    def test_init_default_name(self):
        from sales.printer import ImpresoraTermica
        p = ImpresoraTermica()
        assert p.nombre_impresora == "POS-80-Series"

    # TEST: init con nombre personalizado
    def test_init_custom_name(self, printer):
        assert printer.nombre_impresora == "TEST_PRINTER"

    # TEST: _encode devuelve bytes
    def test_encode(self, printer):
        result = printer._encode("Hola Mundo")
        assert isinstance(result, bytes)
        assert result == b"Hola Mundo"

    # TEST: _encode reemplaza caracteres no cp437
    def test_encode_replace(self, printer):
        result = printer._encode("ñandú")
        assert isinstance(result, bytes)

    # TEST: _generar_ticket retorna bytes con datos minimos
    def test_generar_ticket_minimo(self, printer):
        datos = {"folio": "001-001", "total": "100.00"}
        ticket = printer._generar_ticket(datos)
        assert isinstance(ticket, bytes)
        assert len(ticket) > 0
        assert b"NOTA DE VENTA" in ticket
        assert b"001-001" in ticket

    # TEST: _generar_ticket con todos los datos
    def test_generar_ticket_completo(self, printer):
        datos = {
            "folio": "001-001", "fecha": "01/01/25 12:00",
            "vendedor": "Juan", "cliente": "Pedro Lopez",
            "subtotal": 200.00, "descuento": 20.00, "total": 180.00,
            "adelanto": 0, "metodo_pago": "",
            "productos": [{"cantidad": 2, "nombre": "Producto A", "subtotal": 100.00, "descuento": 0}],
        }
        ticket = printer._generar_ticket(datos)
        assert isinstance(ticket, bytes)
        assert b"Juan" in ticket
        assert b"Pedro Lopez" in ticket
        assert b"Producto A" in ticket
        assert b"180.00" in ticket

    # TEST: _generar_ticket con descuento
    def test_generar_ticket_descuento(self, printer):
        datos = {
            "folio": "001", "total": 90.00, "subtotal": 100.00, "descuento": 10.00,
            "productos": [{"cantidad": 1, "nombre": "Test", "subtotal": 100.00, "descuento": 10}],
        }
        ticket = printer._generar_ticket(datos)
        assert b"Desc:" in ticket or b"S/10.00" in ticket

    # TEST: _generar_ticket con adelanto parcial
    def test_generar_ticket_adelanto_parcial(self, printer):
        datos = {
            "folio": "001", "total": 200.00, "subtotal": 200.00, "descuento": 0,
            "adelanto": 50.00, "metodo_pago": "EFECTIVO",
            "productos": [],
        }
        ticket = printer._generar_ticket(datos)
        assert b"PENDIENTE DE CANCELAR" in ticket

    # TEST: _generar_ticket con adelanto completo
    def test_generar_ticket_adelanto_completo(self, printer):
        datos = {
            "folio": "001", "total": 200.00, "subtotal": 200.00, "descuento": 0,
            "adelanto": 200.00, "metodo_pago": "TARJETA",
            "productos": [],
        }
        ticket = printer._generar_ticket(datos)
        assert b"CANCELADO" in ticket

    # TEST: _generar_ticket con observaciones
    def test_generar_ticket_observaciones(self, printer):
        datos = {
            "folio": "001", "total": 100.00, "subtotal": 100.00, "descuento": 0,
            "observaciones": "Gracias por su compra",
            "productos": [],
        }
        ticket = printer._generar_ticket(datos)
        assert b"Gracias por su compra" in ticket

    # TEST: _generar_ticket con OpticalCenter en BD
    def test_generar_ticket_con_optical_center(self, printer):
        from opticalCenter.models import OpticalCenter
        OpticalCenter.objects.create(optNom="Optica Test", optDir="Av Principal 123", optTel="999888777")
        datos = {"folio": "001", "total": 50.00, "subtotal": 50.00, "descuento": 0, "productos": []}
        ticket = printer._generar_ticket(datos)
        assert b"Optica Test" in ticket
        assert b"AV PRINCIPAL 123" in ticket
        assert b"999888777" in ticket

    # TEST: _generar_ticket sin OpticalCenter usa fallback
    def test_generar_ticket_sin_optical_center(self, printer):
        datos = {"folio": "001", "total": 50.00, "subtotal": 50.00, "descuento": 0, "productos": []}
        ticket = printer._generar_ticket(datos)
        assert b"OPTICA VISION IDEAL" in ticket

    # TEST: _generar_ticket con producto multilinea (lunas)
    def test_generar_ticket_producto_multilinea(self, printer):
        datos = {
            "folio": "001", "total": 300.00, "subtotal": 300.00, "descuento": 0,
            "productos": [{"cantidad": 1, "nombre": "Luna Personalizada\nOD: -1.50\nOI: -2.00", "subtotal": 300.00, "descuento": 0}],
        }
        ticket = printer._generar_ticket(datos)
        assert b"Luna Personalizada" in ticket
        assert b"-1.50" in ticket

    # TEST: _preparar_logo_termico crea archivo temporal
    def test_preparar_logo_termico(self, printer):
        from PIL import Image
        import tempfile, os
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
        img = Image.new("RGB", (100, 50), color="white")
        img.save(tmp.name)
        tmp.close()
        result = printer._preparar_logo_termico(tmp.name, ancho_max=576)
        assert os.path.exists(result)
        assert result.endswith(".png")
        os.unlink(tmp.name)
        if os.path.exists(result):
            os.unlink(result)

    # TEST: _convertir_imagen_a_escpos devuelve bytes
    def test_convertir_imagen_a_escpos(self, printer):
        from PIL import Image
        import tempfile, os
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
        img = Image.new("RGB", (50, 30), color="black")
        img.save(tmp.name)
        tmp.close()
        result = printer._convertir_imagen_a_escpos(tmp.name, ancho_max=100)
        assert isinstance(result, bytes)
        assert len(result) > 0
        os.unlink(tmp.name)

    # TEST: _convertir_imagen_a_escpos con logo inexistente lanza FileNotFoundError
    def test_convertir_imagen_a_escpos_sin_archivo(self, printer):
        with pytest.raises(FileNotFoundError):
            printer._convertir_imagen_a_escpos("/no/existe.png")

    # TEST: imprimir_ticket_venta exito
    def test_imprimir_ticket_venta_success(self, printer):
        with patch.object(printer, '_enviar_a_impresora', return_value={'success': True}):
            result = printer.imprimir_ticket_venta({"folio": "001", "total": 100.00, "subtotal": 100.00, "descuento": 0, "productos": []})
            assert result['success'] is True

    # TEST: imprimir_ticket_venta captura excepcion
    def test_imprimir_ticket_venta_error(self, printer):
        with patch.object(printer, '_generar_ticket', side_effect=Exception("Fallo")):
            result = printer.imprimir_ticket_venta({})
            assert result['success'] is False
            assert "Fallo" in result['error']

    # TEST: _enviar_a_impresora con subprocess exitoso
    def test_enviar_a_impresora_exito(self, printer):
        mock_run = MagicMock()
        mock_run.returncode = 0
        with patch('subprocess.run', return_value=mock_run):
            result = printer._enviar_a_impresora(b"test data")
            assert result['success'] is True

    # TEST: _enviar_a_impresora con subprocess fallido
    def test_enviar_a_impresora_fallo(self, printer):
        mock_run = MagicMock()
        mock_run.returncode = 1
        with patch('subprocess.run', return_value=mock_run):
            result = printer._enviar_a_impresora(b"test data")
            assert result['success'] is False

    # TEST: _generar_ticket con producto con descuento
    def test_generar_ticket_producto_con_descuento(self, printer):
        datos = {
            "folio": "001", "total": 80.00, "subtotal": 100.00, "descuento": 20.00,
            "productos": [{"cantidad": 1, "nombre": "Prod Desc", "subtotal": 100.00, "descuento": 20}],
        }
        ticket = printer._generar_ticket(datos)
        assert b"Desc:" in ticket

    # TEST: _generar_ticket con logo en OpticalCenter
    def test_generar_ticket_con_logo(self, printer):
        from opticalCenter.models import OpticalCenter
        from PIL import Image
        import tempfile, os
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
        img = Image.new("RGB", (200, 60), color="white")
        img.save(tmp.name)
        tmp.close()
        oc = OpticalCenter.objects.create(optNom="Optica Logo")
        oc.optLogo.name = tmp.name
        oc.save()
        datos = {"folio": "001", "total": 100.00, "subtotal": 100.00, "descuento": 0, "productos": []}
        ticket = printer._generar_ticket(datos)
        assert isinstance(ticket, bytes)
        os.unlink(tmp.name)

    # TEST: _generar_ticket con total decimal y fecha real
    def test_generar_ticket_total_decimal(self, printer):
        from datetime import datetime
        datos = {
            "folio": "001", "total": 99.99, "subtotal": 99.99, "descuento": 0,
            "fecha": datetime.now().strftime("%d/%m/%y %H:%M"),
            "productos": [{"cantidad": 1, "nombre": "Articulo", "subtotal": 99.99, "descuento": 0}],
        }
        ticket = printer._generar_ticket(datos)
        assert b"99.99" in ticket
