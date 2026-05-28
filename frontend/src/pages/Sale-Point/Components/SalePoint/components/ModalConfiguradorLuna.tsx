import React, { useState, useEffect } from 'react';
import { X, Eye, DollarSign, Loader2, AlertCircle } from 'lucide-react';
import { lunaService } from '../../../../../auth/services/luna/lunaService';
import type {
  LunaMaterial,
  LunaTipo,
  LunaCaracteristica,
  LunaConfiguracion
} from '../../../../../auth/services/luna/lunaService';
import { showErrorToast } from '../../../../../utils/sweetAlertConfig';

export interface LunaConfiguracionData {
  lunConfCod: number;
  materialNombre: string;
  tipoNombre: string;
  caracteristicasIds: number[];
  caracteristicasNombres: string[];
  precioBase: number;
  precioCaracteristicas: number;
  precioTotal: number;
  precioVentaManual?: number;  // Permite override
}

interface ModalConfiguradorLunaProps {
  isOpen: boolean;
  onClose: () => void;
  onConfirm: (config: LunaConfiguracionData) => void;
}

const ModalConfiguradorLuna: React.FC<ModalConfiguradorLunaProps> = ({
  isOpen,
  onClose,
  onConfirm
}) => {
  // ==================== ESTADO ====================
  const [loading, setLoading] = useState(true);
  const [calculando, setCalculando] = useState(false);
  
  // Catálogos
  const [materiales, setMateriales] = useState<LunaMaterial[]>([]);
  const [tipos, setTipos] = useState<LunaTipo[]>([]);
  const [caracteristicas, setCaracteristicas] = useState<LunaCaracteristica[]>([]);
  
  // Selección
  const [materialSeleccionado, setMaterialSeleccionado] = useState<number | null>(null);
  const [tipoSeleccionado, setTipoSeleccionado] = useState<number | null>(null);
  const [caracteristicasSeleccionadas, setCaracteristicasSeleccionadas] = useState<number[]>([]);
  
  // Configuración y precios
  const [configuracion, setConfiguracion] = useState<LunaConfiguracion | null>(null);
  const [precioSugerido, setPrecioSugerido] = useState<number>(0);
  const [precioManual, setPrecioManual] = useState<string>('');

  // ==================== CARGAR CATÁLOGOS ====================
  useEffect(() => {
    if (isOpen) {
      // Resetear estado completamente al abrir
      setConfiguracion(null);
      setPrecioSugerido(0);
      setPrecioManual('');
      setCaracteristicasSeleccionadas([]);
      
      cargarCatalogos();
    }
  }, [isOpen]);

  // ==================== DETECTAR TECLA ESC ====================
  useEffect(() => {
    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape' && isOpen) {
        handleCancel();
      }
    };

    if (isOpen) {
      document.addEventListener('keydown', handleEscape);
    }

    return () => {
      document.removeEventListener('keydown', handleEscape);
    };
  }, [isOpen]);

  const cargarCatalogos = async () => {
    try {
      setLoading(true);
      const [matsData, tipsData, carsData] = await Promise.all([
        lunaService.getMateriales(),
        lunaService.getTipos(),
        lunaService.getCaracteristicas()
      ]);

      // Ordenar materiales: NK, Policarbonato, Resina, Cristal, Otros
      const ordenMateriales = ['NK', 'Policarbonato', 'Resina', 'Cristal', 'Otros'];
      const materialesOrdenados = matsData.sort((a, b) => {
        const indexA = ordenMateriales.indexOf(a.lunMatNombre);
        const indexB = ordenMateriales.indexOf(b.lunMatNombre);
        if (indexA === -1) return 1;
        if (indexB === -1) return -1;
        return indexA - indexB;
      });

      // Ordenar tipos: Monofocal, Bifocal, Multifocal
      const ordenTipos = ['Monofocal', 'Bifocal', 'Multifocal'];
      const tiposOrdenados = tipsData.sort((a, b) => {
        const indexA = ordenTipos.indexOf(a.lunTipNombre);
        const indexB = ordenTipos.indexOf(b.lunTipNombre);
        if (indexA === -1) return 1;
        if (indexB === -1) return -1;
        return indexA - indexB;
      });

      // Ordenar características: Blue Block, UV-400, y los demás
      const caracteristicasPrioritarias = ['AR', 'UV-400', 'Blue Block'];
      const caracteristicasOrdenadas = carsData.sort((a, b) => {
        const indexA = caracteristicasPrioritarias.indexOf(a.lunCarNombre);
        const indexB = caracteristicasPrioritarias.indexOf(b.lunCarNombre);
        
        // Si ambos están en la lista prioritaria
        if (indexA !== -1 && indexB !== -1) return indexA - indexB;
        // Si solo A está en la lista prioritaria
        if (indexA !== -1) return -1;
        // Si solo B está en la lista prioritaria
        if (indexB !== -1) return 1;
        // Si ninguno está en la lista, mantener orden alfabético
        return a.lunCarNombre.localeCompare(b.lunCarNombre);
      });

      setMateriales(materialesOrdenados);
      setTipos(tiposOrdenados);
      setCaracteristicas(caracteristicasOrdenadas);

      // Seleccionar primeros por defecto
      if (materialesOrdenados.length > 0) setMaterialSeleccionado(materialesOrdenados[0].lunMatCod);
      if (tiposOrdenados.length > 0) setTipoSeleccionado(tiposOrdenados[0].lunTipCod);
      
      // Marcar por defecto: NK Monofocal, UV-400 y Blue block
      const caracteristicasDefault = caracteristicasOrdenadas
        .filter(c => {
          const nombre = c.lunCarNombre.toLowerCase().trim();
          return nombre === 'nk monofocal' || 
                 nombre === 'uv-400' || 
                 nombre === 'blue block' ||
                 nombre === 'ar';
        })
        .map(c => c.lunCarCod);
      setCaracteristicasSeleccionadas(caracteristicasDefault);
    } catch (error) {
      console.error('Error cargando catálogos:', error);
      showErrorToast('Error al cargar datos de lunas');
    } finally {
      setLoading(false);
    }
  };

  // ==================== OBTENER CONFIGURACIÓN ====================
  useEffect(() => {
    if (materialSeleccionado && tipoSeleccionado && !loading) {
      obtenerConfiguracion();
    }
  }, [materialSeleccionado, tipoSeleccionado, loading]);

  const obtenerConfiguracion = async () => {
    if (!materialSeleccionado || !tipoSeleccionado) return;

    try {
      const config = await lunaService.getConfiguracion(materialSeleccionado, tipoSeleccionado);
      setConfiguracion(config);
      calcularPrecioTotal(config.lunConfCod, caracteristicasSeleccionadas);
    } catch (error) {
      showErrorToast('Error al obtener configuración');
    }
  };

  // ==================== CALCULAR PRECIO ====================
  useEffect(() => {
    if (configuracion) {
      calcularPrecioTotal(configuracion.lunConfCod, caracteristicasSeleccionadas);
    }
  }, [caracteristicasSeleccionadas]);

  const calcularPrecioTotal = async (lunConfCod: number, caracteristicasIds: number[]) => {
    try {
      setCalculando(true);
      const resultado = await lunaService.calcularPrecio({
        lunConfCod,
        caracteristicas: caracteristicasIds
      });
      setPrecioSugerido(resultado.precio_total);
      
      // No pre-llenar el precio manual, dejarlo vacío
    } catch (error) {
      console.error('Error calculando precio:', error);
    } finally {
      setCalculando(false);
    }
  };

  // ==================== TOGGLE CARACTERÍSTICA ====================
  const toggleCaracteristica = (id: number) => {
    setCaracteristicasSeleccionadas(prev => 
      prev.includes(id) 
        ? prev.filter(x => x !== id)
        : [...prev, id]
    );
  };

  // ==================== CONFIRMAR ====================
  const handleConfirm = () => {
    if (!materialSeleccionado || !tipoSeleccionado || !configuracion) {
      showErrorToast('Selecciona Material y Tipo');
      return;
    }

    // Validar que el usuario haya ingresado un precio manualmente
    if (!precioManual || precioManual.trim() === '') {
      showErrorToast('Por favor, ingresa un precio de venta');
      return;
    }

    const precioFinal = parseFloat(precioManual);

    if (isNaN(precioFinal) || precioFinal <= 0) {
      showErrorToast('El precio debe ser mayor a 0');
      return;
    }

    const material = materiales.find(m => m.lunMatCod === materialSeleccionado);
    const tipo = tipos.find(t => t.lunTipCod === tipoSeleccionado);
    const caracteristicasNombres = caracteristicas
      .filter(c => caracteristicasSeleccionadas.includes(c.lunCarCod))
      .map(c => c.lunCarNombre);

    const config: LunaConfiguracionData = {
      lunConfCod: configuracion.lunConfCod,
      materialNombre: material?.lunMatNombre || '',
      tipoNombre: tipo?.lunTipNombre || '',
      caracteristicasIds: caracteristicasSeleccionadas,
      caracteristicasNombres,
      precioBase: configuracion.lunConfPrecioBase,
      precioCaracteristicas: precioSugerido - configuracion.lunConfPrecioBase,
      precioTotal: precioFinal,
      precioVentaManual: precioFinal
    };

    onConfirm(config);
    handleCancel();
  };

  // ==================== CANCELAR ====================
  const handleCancel = () => {
    // Solo cerrar, el reset se hace en useEffect cuando se abre de nuevo
    onClose();
  };

  // ==================== RENDER ====================
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-2xl max-w-lg w-full max-h-[85vh] overflow-y-auto border-2 border-gray-200">
        {/* Header */}
        <div className="sticky top-0 bg-blue-500 text-white px-3 py-2 rounded-t-lg flex justify-between items-center z-10">
          <div className="flex items-center gap-2">
            <h2 className="text-sm font-bold">Personalizacion de Luna</h2>
          </div>
          <button
            onClick={handleCancel}
            className="hover:bg-white hover:bg-opacity-20 p-1 rounded transition-colors"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Body */}
        <div className="p-3 space-y-3">
          {loading ? (
            <div className="flex flex-col items-center justify-center py-8">
              <Loader2 className="w-8 h-8 text-blue-500 animate-spin" />
              <p className="mt-2 text-xs text-gray-600">Cargando...</p>
            </div>
          ) : (
            <>
              {/* Material */}
              <div>
                <label className="block text-xs font-semibold text-gray-700 mb-1.5">
                  Material <span className="text-red-500">*</span>
                </label>
                <div className="grid grid-cols-5 gap-1.5">
                  {materiales.map((mat) => (
                    <button
                      key={mat.lunMatCod}
                      onClick={() => setMaterialSeleccionado(mat.lunMatCod)}
                      className={`
                        px-2 py-1.5 rounded border font-medium transition-all text-xs
                        ${materialSeleccionado === mat.lunMatCod
                          ? 'border-blue-500 bg-blue-50 text-blue-700'
                          : 'border-gray-200 hover:border-blue-300 hover:bg-gray-50'
                        }
                      `}
                      title={mat.lunMatDescripcion}
                    >
                      {mat.lunMatNombre}
                    </button>
                  ))}
                </div>
              </div>

              {/* Tipo */}
              <div>
                <label className="block text-xs font-semibold text-gray-700 mb-1.5">
                  Tipo de Luna <span className="text-red-500">*</span>
                </label>
                <div className="grid grid-cols-3 gap-1.5">
                  {tipos.map((t) => (
                    <button
                      key={t.lunTipCod}
                      onClick={() => setTipoSeleccionado(t.lunTipCod)}
                      className={`
                        px-2 py-1.5 rounded border font-medium transition-all text-xs
                        ${tipoSeleccionado === t.lunTipCod
                          ? 'border-blue-500 bg-blue-50 text-blue-700'
                          : 'border-gray-200 hover:border-blue-300 hover:bg-gray-50'
                        }
                      `}
                      title={t.lunTipDescripcion}
                    >
                      {t.lunTipNombre}
                    </button>
                  ))}
                </div>
              </div>

              {/* Características */}
              <div>
                <label className="block text-xs font-semibold text-gray-700 mb-1.5">
                  Características Adicionales
                </label>
                <div className="grid grid-cols-2 gap-1.5">
                  {caracteristicas.map((caract) => (
                    <button
                      key={caract.lunCarCod}
                      onClick={() => toggleCaracteristica(caract.lunCarCod)}
                      className={`
                        px-2 py-1.5 rounded border font-medium transition-all text-xs text-left
                        ${caracteristicasSeleccionadas.includes(caract.lunCarCod)
                          ? 'border-blue-500 bg-blue-50 text-blue-700'
                          : 'border-gray-200 hover:border-blue-300 hover:bg-gray-50'
                        }
                      `}
                      title={caract.lunCarDescripcion}
                    >
                      {caract.lunCarNombre}
                    </button>
                  ))}
                </div>
              </div>

              {/* Precio de Venta */}
              <div>
                <label className="block text-xs font-semibold text-gray-700 mb-1.5">
                  Precio de Venta <span className="text-red-500">*</span>
                </label>
                <input
                  type="number"
                  step="0.01"
                  min="0"
                  value={precioManual}
                  onChange={(e) => setPrecioManual(e.target.value)}
                  placeholder="Ingresa el precio"
                  required
                  className={`w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 transition-colors ${
                    precioManual ? 'border-gray-300 focus:ring-blue-500 focus:border-blue-500' : 'border-red-300 focus:ring-red-500 focus:border-red-500'
                  }`}
                />
                {!precioManual && (
                  <p className="text-xs text-red-600 mt-1">* Campo obligatorio</p>
                )}
              </div>
            </>
          )}
        </div>

        {/* Footer */}
        <div className="sticky bottom-0 bg-gray-50 px-3 py-2 rounded-b-lg flex gap-2 border-t">
          <button
            onClick={handleCancel}
            className="flex-1 px-3 py-1.5 border border-gray-300 rounded text-xs font-semibold text-gray-700 hover:bg-gray-100 transition-colors"
          >
            Cancelar
          </button>
          <button
            onClick={handleConfirm}
            disabled={loading || !configuracion}
            className="flex-1 px-3 py-1.5 bg-blue-500 text-white rounded text-xs font-semibold hover:bg-blue-600 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Agregar
          </button>
        </div>
      </div>
    </div>
  );
};

export default ModalConfiguradorLuna;
