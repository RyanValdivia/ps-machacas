import subprocess
import tempfile
import os
from datetime import datetime
from PIL import Image, ImageOps
from django.conf import settings


class ImpresoraTermica:
    """Maneja impresión en impresora térmica usando ESC/POS"""
    
    def __init__(self, nombre_impresora="POS-80-Series"):
        self.nombre_impresora = nombre_impresora
        self.ESC = b'\x1b'
        self.GS = b'\x1d'
    
    def imprimir_ticket_venta(self, datos_venta):
        try:
            comandos = self._generar_ticket(datos_venta)
            return self._enviar_a_impresora(comandos)
        except Exception as e:
            return {'success': False, 'error': f'Error al imprimir: {str(e)}'}
    
    def _generar_ticket(self, datos):
        ticket = b''
        
        # ========== INICIALIZAR ==========
        ticket += self.ESC + b'@'
        ticket += self.ESC + b'3\x00'
        ticket += self.ESC + b'a\x01'  # Centrar
        
        # Obtener datos de la óptica
        from opticalCenter.models import OpticalCenter
        optical_center = OpticalCenter.objects.first()
        
        # ========== LOGO CON MARGEN ==========
        if optical_center and optical_center.optLogo:

            logo_path = os.path.join(settings.MEDIA_ROOT, str(optical_center.optLogo))
            if os.path.exists(logo_path):
                ticket += b'  '  # Margen izquierdo
                ticket += self.ESC + b'a\x01'
                logo_cmd = self._convertir_imagen_a_escpos(logo_path, ancho_max=600)  # Casi todo el ancho (25% más que 550)
                if logo_cmd:
                    ticket += logo_cmd
                ticket += self.ESC + b'a\x00'
        
        # ========== NOMBRE CON MARGEN ==========
        ticket += b'  '  # Margen izquierdo
        if optical_center and optical_center.optNom:
            ticket += self._encode(f"{optical_center.optNom}\n")
        else:
            ticket += self._encode("OPTICA VISION IDEAL\n")
        
        # Dirección con margen
        if optical_center and optical_center.optDir:
            ticket += b'  '  # Margen izquierdo
            ticket += self.ESC + b'!\x08'
            ticket += self._encode(f"{optical_center.optDir.upper()}\n")
            ticket += self.ESC + b'!\x00'
        
        # Teléfono con margen
        if optical_center and optical_center.optTel:
            ticket += b'  '  # Margen izquierdo
            ticket += self.ESC + b'!\x08'
            ticket += self._encode(f"TEL: {optical_center.optTel}\n")
            ticket += self.ESC + b'!\x00'
        
        ticket += b'  ' + b'=' * 44 + b'\n'  # Margen + separador
        
        # ========== TITULO ==========
        ticket += self.ESC + b'a\x01'
        ticket += self.ESC + b'!\x08'
        ticket += self._encode("NOTA DE VENTA\n")
        ticket += self._encode("RUC : 10296530722\n")
        ticket += self.ESC + b'!\x00'
        ticket += self.ESC + b'a\x00'
        ticket += b'  ' + b'-' * 44 + b'\n'  # Margen + separador
        
        # ========== INFO ==========
        ticket += b'  ' + self._encode(f"Nro: {datos.get('folio','N/A')}\n")
        ticket += b'  ' + self._encode(f"Fecha Emision: {datos.get('fecha', datetime.now().strftime('%d/%m/%y %H:%M'))}\n")
        
        if datos.get('vendedor'):
            ticket += b'  ' + self._encode(f"Atendió: {datos['vendedor']}\n")
        if datos.get('cliente'):
            ticket += b'  ' + self._encode(f"Cliente: {datos['cliente']}\n")
        
        ticket += b'  ' + b'-' * 44 + b'\n'  # Margen + separador
        
        # ========== PRODUCTOS ==========
        ticket += b'  ' + self.ESC + b'!\x08'
        ticket += b'CANT DESCRIPCION                IMPORTE\n'
        ticket += self.ESC + b'!\x00'
        ticket += b'  ' + b'-' * 44 + b'\n'  # Margen + separador
        
        for p in datos.get('productos', []):
            cant = str(p['cantidad']).ljust(5)
            nombre_completo = p['nombre']
            precio = f"S/{float(p.get('subtotal',0)):.2f}".rjust(9)
            
            # Si el nombre tiene saltos de línea (detalles de luna)
            if '\n' in str(nombre_completo):
                partes = str(nombre_completo).split('\n')
                # Primera línea con cantidad y precio
                nombre_primera = partes[0][:26].ljust(26)
                ticket += b'  ' + self._encode(f"{cant}{nombre_primera}{precio}\n")
                # Líneas adicionales con margen
                for parte in partes[1:]:
                    ticket += b'  ' + self._encode(f"     {parte[:39]}\n")
            else:
                nombre = nombre_completo[:26].ljust(26)
                ticket += b'  ' + self._encode(f"{cant}{nombre}{precio}\n")
            
            # Descuento si existe (con margen)
            if p.get('descuento', 0) > 0:
                ticket += b'  ' + self._encode(f"     Desc: -S/{float(p['descuento']):.2f}\n")
            
            ticket += b'  ' + b'-' * 44 + b'\n'  # Margen + separador
        
        # ========== TOTALES ==========
        ticket += self.ESC + b'a\x02'
        ticket += self._encode(f"Subtotal General: S/{float(datos.get('subtotal',0)):.2f}\n")
        
        if datos.get('descuento',0) > 0:
            ticket += self._encode(f"Desc: -S/{float(datos['descuento']):.2f}\n")
        
        ticket += self.ESC + b'!\x10'
        ticket += self._encode(f"TOTAL: S/{float(datos.get('total',0)):.2f}\n")
        ticket += self.ESC + b'!\x00'
        
        # Mostrar información de pago
        adelanto = float(datos.get('adelanto', 0))
        total = float(datos.get('total', 0))
        saldo = total - adelanto
        
        if adelanto > 0:
            ticket += self._encode(f"Adelanto: S/{adelanto:.2f}\n")
            
            if saldo > 0:
                ticket += self._encode(f"Saldo: S/{saldo:.2f}\n")
                # Mostrar "A CUENTA" cuando hay saldo pendiente
                ticket += self.ESC + b'a\x01'
                ticket += self.ESC + b'!\x10'
                ticket += self._encode("PENDIENTE DE CANCELAR\n")
                ticket += self.ESC + b'!\x00'
                ticket += self.ESC + b'a\x02'
            else:
                # Mostrar "CANCELADO" cuando está totalmente pagado
                ticket += self.ESC + b'a\x01'
                ticket += self.ESC + b'!\x10'
                ticket += self._encode("CANCELADO\n")
                ticket += self.ESC + b'!\x00'
                ticket += self.ESC + b'a\x02'
            
            if datos.get('metodo_pago'):
                ticket += self._encode(f"{datos['metodo_pago']}\n")

        
        # ========== PIE ==========
        ticket += self.ESC + b'a\x01'
        
        # Observaciones si existen
        if datos.get('observaciones'):
            ticket += b'\n'
            ticket += self._encode('OBS:\n')
            ticket += self._encode(f"{datos['observaciones']}\n")
        
        ticket += b'\n'
        ticket += self._encode("Representación impresa de Nota de Venta\n")
        ticket += self._encode("Es normal notar cierto mareo y hasta dolor de cabeza durante primeros días, si persiste por favor acuda a una revision con nosotros.\n")
        ticket += self._encode("Gracias por su compra!\n")
        ticket += b'\n' * 4  # Espacio suficiente para que salga del cabezal
        
        # Comando de corte completo
        ticket += self.GS + b'V\x01'
        return ticket
    
    def _encode(self, texto):
        return texto.encode('cp437', errors='replace')
    
    def _preparar_logo_termico(self, logo_path, ancho_max=576):
        img = Image.open(logo_path).convert("L")
        img = ImageOps.expand(img, border=(20,0,0,0), fill=255) #Centrado
        img = ImageOps.autocontrast(img)
        if img.width > ancho_max:
            ratio = ancho_max / img.width
            img = img.resize((ancho_max, int(img.height * ratio)), Image.Resampling.LANCZOS)
        img = img.convert('1')
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
        img.save(tmp.name)
        return tmp.name
    
    def _convertir_imagen_a_escpos(self, imagen_path, ancho_max=1400):
        tmp = self._preparar_logo_termico(imagen_path, ancho_max)
        img = Image.open(tmp)
        pixels = list(img.getdata())
        w, h = img.size
        w_bytes = (w + 7) // 8
        
        data = self.GS + b'v0\x00'
        data += bytes([w_bytes & 0xFF, (w_bytes >> 8) & 0xFF])
        data += bytes([h & 0xFF, (h >> 8) & 0xFF])
        
        for y in range(h):
            for x in range(0, w, 8):
                byte = 0
                for bit in range(8):
                    if x + bit < w and pixels[y * w + x + bit] == 0:
                        byte |= 1 << (7 - bit)
                data += bytes([byte])
        
        os.unlink(tmp)
        return data + b'\n'
    
    def _enviar_a_impresora(self, comandos):
        with tempfile.NamedTemporaryFile(delete=False, suffix=".prn") as f:
            f.write(comandos)
            path = f.name
        
        cmd = f'copy /b "{path}" "\\\\localhost\\POS80"'
        res = subprocess.run(cmd, shell=True, capture_output=True)
        os.unlink(path)
        
        return {'success': res.returncode == 0}
