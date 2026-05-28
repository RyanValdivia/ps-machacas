import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { X, Edit2, Trash2, Plus, ChevronDown, ChevronUp, Eye } from "lucide-react";
import type { Client } from "../../../../types/client";
import type { Prescription } from "../../../../types/prescription";
import { deleteClient } from "../../../../services/clientService";
import { getRecipes } from "../../../../services/prescriptionService";
import { saleService } from "../../../../auth/services/sale/saleService";
import type { VentaResponse } from "../../../../auth/types/sale/sale";
import PrescriptionForm from "../../PrescriptionForm";

type Props = {
  client: Client | null;
  open: boolean;
  onClose: () => void;
  onEdit: (client: Client) => void;
  onRefresh: () => void;
};

const ClientDetailPanel = ({ client, open, onClose, onEdit, onRefresh }: Props) => {
  const navigate = useNavigate();
  const [showAllPrescriptions, setShowAllPrescriptions] = useState(false);
  const [expandedPrescriptionId, setExpandedPrescriptionId] = useState<number | null>(null);
  const [showPrescriptionForm, setShowPrescriptionForm] = useState(false);
  const [prescriptions, setPrescriptions] = useState<Prescription[]>([]);
  const [loadingPrescriptions, setLoadingPrescriptions] = useState(false);
  const [prescriptionToEdit, setPrescriptionToEdit] =useState<Prescription>();
  const [latestSale, setLatestSale] = useState<VentaResponse | null>(null);
  const [loadingSales, setLoadingSales] = useState(false);

  useEffect(() => {
    if (open && client) { //Error aqui0
      loadPrescriptions();
      loadSales();
    }
    else{
      console.log("No se esta actualizando el open y el client")
    }
  }, [open, client]);

  const loadPrescriptions = async () => { 
    if (!client) {
      return;
    }
    
    setLoadingPrescriptions(true);
    try {
      const data = await getRecipes(1, { cliCod: client.cliCod });
      setPrescriptions(data.results);
    } catch (error) {
      console.error("Error cargando recetas:", error);
      setPrescriptions([]);
    } finally {
      setLoadingPrescriptions(false);
    }
  };

  const loadSales = async () => {
    if (!client) {
      return;
    }
    
    setLoadingSales(true);
    try {
      const data = await saleService.getAll({
        search: client.cliNumDoc,
        page: 1,
        page_size: 1
      });
      
      if (data.results && data.results.length > 0) {
        setLatestSale(data.results[0]);
      } else {
        setLatestSale(null);
      }
    } catch (error) {
      console.error("Error cargando ventas:", error);
      setLatestSale(null);
    } finally {
      setLoadingSales(false);
    }
  };

  const handleViewAllSales = () => {
    if (!client) return;
    navigate(`/sales?search=${encodeURIComponent(client.cliNumDoc)}`);
    onClose();
  };

  if (!client || !open) return null;

  const formatDate = (dateString: string | null | undefined) => {
    if (!dateString) return "N/A";

    // Si es un string con formato ISO (puede incluir hora)
    if (typeof dateString === "string" && dateString.match(/^\d{4}-\d{2}-\d{2}/)) {
      // Extraer solo la parte de la fecha (antes de 'T' si existe)
      const datePart = dateString.split("T")[0];
      const [year, month, day] = datePart.split("-");
      return `${day}/${month}/${year}`;
    }

    const date = new Date(dateString);
    if (isNaN(date.getTime())) return "N/A";

    const day = String(date.getDate()).padStart(2, "0");
    const month = String(date.getMonth() + 1).padStart(2, "0");
    const year = date.getFullYear();
    return `${day}/${month}/${year}`;
  };

  const formatDateTime = (dateString: string | null | undefined) => {
    if (!dateString) return "N/A";

    const date = new Date(dateString);
    if (isNaN(date.getTime())) return "N/A";

    const day = String(date.getDate()).padStart(2, "0");
    const month = String(date.getMonth() + 1).padStart(2, "0");
    const year = date.getFullYear();
    const hours = String(date.getHours()).padStart(2, "0");
    const minutes = String(date.getMinutes()).padStart(2, "0");
    
    return `${day}/${month}/${year} ${hours}:${minutes}`;
  };

  const calculateAge = (birthDate: string | null | undefined): number | null => {
    if (!birthDate) return null;
    
    const today = new Date();
    const birth = new Date(birthDate);
    
    if (isNaN(birth.getTime())) return null;
    
    let age = today.getFullYear() - birth.getFullYear();
    const monthDiff = today.getMonth() - birth.getMonth();
    
    if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < birth.getDate())) {
      age--;
    }
    
    return age;
  };

  const getClientAge = (): string => {
    // Si ya tiene edad calculada, usarla
    if (client.edad !== null && client.edad !== undefined) {
      return `${client.edad} años`;
    }
    
    // Si no, calcular desde fecha de nacimiento
    if (client.cliFechaNac) {
      const edad = calculateAge(client.cliFechaNac);
      if (edad !== null) {
        return `${edad} años`;
      }
    }
    
    return "No disponible";
  };

  const handleDelete = async () => {
    if (!client) return;

    if (!confirm(`¿Estás seguro de eliminar al cliente ${client.cliNomCompleto}?`)) {
      return;
    }

    try {
      await deleteClient(client.cliCod);
      alert("Cliente eliminado exitosamente");
      onClose();
      onRefresh();
    } catch (error) {
      console.error("Error al eliminar cliente:", error);
      alert("Error al eliminar el cliente");
    }
  };

  const togglePrescription = (id: number) => {
    setExpandedPrescriptionId(expandedPrescriptionId === id ? null : id);
  };

  const handlePrescriptionSuccess = () => {
    setShowPrescriptionForm(false);
    loadPrescriptions();
  };

const parseDate = (date: string) => {
  // Fuerza formato ISO válido
  return new Date(date + "T00:00:00").getTime();
};

const sortedPrescriptions = Array.isArray(prescriptions)
  ? [...prescriptions].sort(
      (a, b) => parseDate(b.recFech) - parseDate(a.recFech)
    )
  : [];

  const latestPrescription = sortedPrescriptions[0];
  const olderPrescriptions = sortedPrescriptions.slice(1);

  return (
    <>
      <div className="fixed inset-0 z-40 flex justify-end">
        {/* Overlay */}
        <div 
          className="flex-1 bg-black/30"
          onClick={onClose}
        />

        {/* Panel derecho */}
        <div className="w-full max-w-xl h-full bg-white shadow-xl border-l border-gray-200 flex flex-col">
          {/* Header Cliente */}
          <div className="flex items-center justify-between px-6 py-4 border-b border-gray-200 bg-gray-50">
            <div>
              <h2 className="text-lg font-semibold text-gray-900">Detalle del cliente</h2>
              <p className="text-sm text-gray-500">Historial de ventas y recetas</p>
            </div>
            <button
              onClick={onClose}
              className="text-gray-400 hover:text-gray-600 transition-colors p-1 rounded-lg hover:bg-gray-100"
              aria-label="Cerrar panel de detalle"
            >
              <X className="w-5 h-5" />
            </button>
          </div>

          {/* Contenido scrollable */}
          <div className="flex-1 overflow-y-auto px-6 py-4 space-y-4">
            {/* Información del cliente */}
            <div className="bg-white rounded-xl p-5 border border-gray-200 shadow-sm flex gap-4">
              <div className="flex h-14 w-14 items-center justify-center rounded-full bg-blue-100 text-blue-700 font-semibold text-lg shrink-0">
                {client.cliNomCompleto?.split(" ").map((p) => p[0]).join("")}
              </div>
              <div className="flex-1 grid grid-cols-2 gap-4 text-sm">
                <div>
                  <p className="text-xs text-gray-500 font-medium mb-1">Nombre completo</p>
                  <p className="font-semibold text-gray-900">{client.cliNomCompleto}</p>
                </div>
                <div>
                  <p className="text-xs text-gray-500 font-medium mb-1">Documento</p>
                  <p className="font-semibold text-gray-900">{client.cliTipoDoc}: {client.cliNumDoc}</p>
                </div>
                <div>
                  <p className="text-xs text-gray-500 font-medium mb-1">Teléfono</p>
                  <p className="font-medium text-gray-800">{client.cliTelef || "No registrado"}</p>
                </div>
                <div>
                  <p className="text-xs text-gray-500 font-medium mb-1">Edad</p>
                  <p className="font-medium text-gray-800">
                    {getClientAge()}
                  </p>
                </div>
              </div>
            </div>

            {/* Última compra */}
            <div className="bg-gray-50 rounded-xl p-4 border border-gray-200">
              <div className="flex items-center justify-between mb-2">
                <p className="text-xs font-semibold text-gray-800 tracking-wide uppercase">Última venta</p>
                <button 
                  onClick={handleViewAllSales}
                  className="text-xs text-blue-600 hover:text-blue-700 font-medium transition-colors"
                >
                  Ver todas las ventas
                </button>
              </div>
              
              {loadingSales ? (
                <div className="text-center py-4">
                  <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600 mx-auto"></div>
                  <p className="text-xs text-gray-500 mt-2">Cargando ventas...</p>
                </div>
              ) : latestSale ? (
                <div className="space-y-3">
                  <div className="grid grid-cols-2 gap-3 text-sm">
                    <div>
                      <p className="text-xs text-gray-500 font-medium mb-1">Fecha y hora</p>
                      <p className="font-semibold text-gray-900">{formatDateTime(latestSale.ventFecha)}</p>
                    </div>
                    <div>
                      <p className="text-xs text-gray-500 font-medium mb-1">Total</p>
                      <p className="font-semibold text-gray-900">S/ {Number(latestSale.ventTotal).toFixed(2)}</p>
                    </div>
                    <div>
                      <p className="text-xs text-gray-500 font-medium mb-1">Estado</p>
                      <span className={`inline-flex items-center rounded-full px-2 py-0.5 text-xs font-semibold ${
                        latestSale.ventEstado === 'PAGADO' 
                          ? 'bg-green-50 text-green-700 border border-green-200'
                          : latestSale.ventEstado === 'PARCIAL'
                          ? 'bg-yellow-50 text-yellow-700 border border-yellow-200'
                          : latestSale.ventEstado === 'ANULADO'
                          ? 'bg-red-50 text-red-700 border border-red-200'
                          : 'bg-gray-50 text-gray-700 border border-gray-200'
                      }`}>
                        {latestSale.estado_pago_display}
                      </span>
                    </div>
                    <div>
                      <p className="text-xs text-gray-500 font-medium mb-1">Pedido</p>
                      <span className={`inline-flex items-center rounded-full px-2 py-0.5 text-xs font-semibold ${
                        latestSale.ventEstadoRecoj === 'ENTREGADO' 
                          ? 'bg-green-50 text-green-700 border border-green-200'
                          : latestSale.ventEstadoRecoj === 'LISTO'
                          ? 'bg-blue-50 text-blue-700 border border-blue-200'
                          : latestSale.ventEstadoRecoj === 'ANULADO'
                          ? 'bg-red-50 text-red-700 border border-red-200'
                          : 'bg-gray-50 text-gray-700 border border-gray-200'
                      }`}>
                        {latestSale.estado_pedido_display}
                      </span>
                    </div>
                  </div>
                  {Number(latestSale.ventSaldo) > 0 && (
                    <div className="bg-yellow-50 border border-yellow-200 rounded p-2">
                      <p className="text-xs text-yellow-800">
                        <span className="font-semibold">Saldo pendiente:</span> S/ {Number(latestSale.ventSaldo).toFixed(2)}
                      </p>
                    </div>
                  )}
                </div>
              ) : (
                <p className="text-sm text-gray-500 italic">No hay ventas registradas para este cliente.</p>
              )}
            </div>

            {/* Cabecera historial de recetas */}
            <div className="flex items-center justify-between mt-2">
              <p className="text-xs font-semibold text-gray-800 tracking-wide uppercase">Historial de recetas</p>

            </div>

            {/* Recetas */}
            {loadingPrescriptions ? (
              <div className="text-center py-8">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
                <p className="text-sm text-gray-500 mt-2">Cargando recetas...</p>
              </div>
            ) : latestPrescription ? (
              <div className="border border-gray-200 rounded-xl bg-white shadow-sm">
                <div className="bg-gradient-to-r from-emerald-50 to-teal-50 px-4 py-3 border-b border-emerald-100 flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <p className="text-xs font-semibold text-gray-800 tracking-wide uppercase">Última receta</p>
                    <span className="inline-flex items-center rounded-full bg-emerald-50 px-2 py-0.5 text-[10px] font-semibold uppercase text-emerald-700 border border-emerald-100">
                      Activa
                    </span>
                    <button
                      onClick={() => {
                        setShowPrescriptionForm(true);
                        setPrescriptionToEdit(latestPrescription);
                      }}
                      className="flex-1 flex items-center justify-center gap-2 px-4 py-2.5 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium"
                    >
                      <Edit2 className="w-4 h-4" />
                    </button>
                  </div>
                  <span className="text-xs text-gray-600 font-medium">
                    {formatDate(latestPrescription.recFech)}
                  </span>
                </div>

                <div className="p-4 space-y-4">
                  <div className="overflow-x-auto">
                    <table className="w-full text-sm">
                      <thead className="bg-gray-100">
                        <tr>
                          <th className="px-3 py-2 text-left text-xs font-semibold text-gray-700 uppercase"></th>
                          <th className="px-3 py-2 text-center text-xs font-semibold text-gray-700 uppercase">SPH</th>
                          <th className="px-3 py-2 text-center text-xs font-semibold text-gray-700 uppercase">CYL</th>
                          <th className="px-3 py-2 text-center text-xs font-semibold text-gray-700 uppercase">Eje</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-gray-200">
                        <tr className="hover:bg-gray-50">
                          <td className="px-3 py-3 font-medium text-gray-700">OD</td>
                          <td className="px-3 py-3 text-center text-gray-800">{latestPrescription.receEsfeOD || 'N/A'}</td>
                          <td className="px-3 py-3 text-center text-gray-800">{latestPrescription.receCilinOD || 'N/A'}</td>
                          <td className="px-3 py-3 text-center text-gray-800">{latestPrescription.receEjeOD ? `${latestPrescription.receEjeOD}°` : 'N/A'}</td>
                        </tr>
                        <tr className="hover:bg-gray-50">
                          <td className="px-3 py-3 font-medium text-gray-700">OI</td>
                          <td className="px-3 py-3 text-center text-gray-800">{latestPrescription.receEsfeOI || 'N/A'}</td>
                          <td className="px-3 py-3 text-center text-gray-800">{latestPrescription.receCilinOI || 'N/A'}</td>
                          <td className="px-3 py-3 text-center text-gray-800">{latestPrescription.receEjeOI ? `${latestPrescription.receEjeOI}°` : 'N/A'}</td>
                        </tr>
                      </tbody>
                    </table>
                  </div>
                  {/* DIP y ADD */}
                  <div className="grid grid-cols-2 gap-3">
                    {latestPrescription.receDIP && (
                      <div className="bg-blue-50 border border-blue-200 rounded p-3">
                        <p className="text-xs text-blue-800">
                          <span className="font-semibold">DIP (Lejos):</span> {latestPrescription.receDIP} mm
                        </p>
                      </div>
                    )}
                    {latestPrescription.receAdd && (
                      <div className="bg-gray-50 border border-gray-200 rounded p-3">
                        <p className="text-xs text-gray-800">
                          <span className="font-semibold">ADD:</span> {latestPrescription.receAdd}
                        </p>
                      </div>
                    )}
                  </div>

                  <button
                    onClick={() => setShowPrescriptionForm(true)}
                    className="w-full flex items-center justify-center gap-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors text-sm font-medium"
                  >
                    <Plus className="w-4 h-4" />
                    Registrar nueva receta
                  </button>
                </div>
              </div>
            ) : (
              <div className="border border-gray-200 rounded-xl p-8 text-center bg-white">
                <p className="text-gray-500 mb-4">No hay recetas registradas</p>
                <button
                  onClick={() => setShowPrescriptionForm(true)}
                  className="inline-flex items-center gap-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors text-sm font-medium"
                >
                  <Plus className="w-4 h-4" />
                  Registrar primera receta
                </button>
              </div>
            )}

            {/* Recetas anteriores */}
            {olderPrescriptions.length > 0 && (
              <div className="border border-gray-200 rounded-xl bg-white">
                <button
                  type="button"
                  onClick={() => setShowAllPrescriptions(!showAllPrescriptions)}
                  className="w-full bg-slate-50 hover:bg-slate-100 transition-colors px-4 py-3 flex items-center justify-between text-xs font-semibold text-gray-800 tracking-wide"
                >
                  <span>Recetas anteriores ({olderPrescriptions.length})</span>
                  {showAllPrescriptions ? (
                    <ChevronUp className="w-5 h-5 text-gray-500" />
                  ) : (
                    <ChevronDown className="w-5 h-5 text-gray-500" />
                  )}
                </button>

                {showAllPrescriptions && (
                  <div className="p-4 space-y-3">
                    {olderPrescriptions.map((prescription) => (
                      <div key={prescription.recCod} className="border border-gray-200 rounded-lg overflow-hidden">
                        <div className="w-full bg-gray-50 hover:bg-gray-100 transition-colors px-4 py-3 flex items-center justify-between text-sm">
                          <button
                            onClick={() => togglePrescription(prescription.recCod)}
                            className="flex-1 flex items-center justify-between"
                          >
                            <span className="font-medium text-gray-700">
                              {formatDate(prescription.recFech)}
                            </span>
                            <div className="flex items-center gap-2">
                              <Eye className="w-4 h-4 text-gray-500" />
                              {expandedPrescriptionId === prescription.recCod ? (
                                <ChevronUp className="w-4 h-4 text-gray-500" />
                              ) : (
                                <ChevronDown className="w-4 h-4 text-gray-500" />
                              )}
                            </div>
                          </button>
                          
                          {/* Botón de editar */}
                          <button
                            onClick={(e) => {
                              e.stopPropagation();
                              setPrescriptionToEdit(prescription);
                              setShowPrescriptionForm(true);
                            }}
                            className="ml-2 p-2 text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
                            title="Editar receta"
                          >
                            <Edit2 className="w-4 h-4" />
                          </button>
                        </div>

                        {expandedPrescriptionId === prescription.recCod && (
                          <div className="p-4 bg-white border-t border-gray-200">
                            <table className="w-full text-sm">
                              <thead className="bg-gray-100">
                                <tr>
                                  <th className="px-3 py-2 text-left text-xs font-semibold text-gray-700 uppercase"></th>
                                  <th className="px-3 py-2 text-center text-xs font-semibold text-gray-700 uppercase">SPH</th>
                                  <th className="px-3 py-2 text-center text-xs font-semibold text-gray-700 uppercase">CYL</th>
                                  <th className="px-3 py-2 text-center text-xs font-semibold text-gray-700 uppercase">Eje</th>
                                </tr>
                              </thead>
                              <tbody className="divide-y divide-gray-200">
                                <tr>
                                  <td className="px-3 py-2 font-medium text-gray-700">OD</td>
                                  <td className="px-3 py-2 text-center text-gray-800">{prescription.receEsfeOD || 'N/A'}</td>
                                  <td className="px-3 py-2 text-center text-gray-800">{prescription.receCilinOD || 'N/A'}</td>
                                  <td className="px-3 py-2 text-center text-gray-800">{prescription.receEjeOD ? `${prescription.receEjeOD}°` : 'N/A'}</td>
                                </tr>
                                <tr>
                                  <td className="px-3 py-2 font-medium text-gray-700">OI</td>
                                  <td className="px-3 py-2 text-center text-gray-800">{prescription.receEsfeOI || 'N/A'}</td>
                                  <td className="px-3 py-2 text-center text-gray-800">{prescription.receCilinOI || 'N/A'}</td>
                                  <td className="px-3 py-2 text-center text-gray-800">{prescription.receEjeOI ? `${prescription.receEjeOI}°` : 'N/A'}</td>
                                </tr>
                              </tbody>
                            </table>
                            <div className="mt-3 grid grid-cols-2 gap-2">
                              {prescription.receDIP && (
                                <div className="bg-blue-50 border border-blue-200 rounded p-2">
                                  <p className="text-xs text-blue-800">
                                    <span className="font-semibold">DIP (Lejos):</span> {prescription.receDIP} mm
                                  </p>
                                </div>
                              )}
                              {prescription.receAdd && (
                                <div className="bg-yellow-50 border border-yellow-200 rounded p-2">
                                  <p className="text-xs text-yellow-800">
                                    <span className="font-semibold">Adición:</span> {prescription.receAdd}
                                  </p>
                                </div>
                              )}
                            </div>
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                )}
              </div>
)}
          </div>

          {/* Acciones: Editar y Eliminar */}
          <div className="flex gap-3 px-6 py-4 border-t border-gray-200 bg-gray-50">
            <button
              onClick={() => {
                onEdit(client);
                onClose();
              }}
              className="flex-1 flex items-center justify-center gap-2 px-4 py-2.5 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium"
            >
              <Edit2 className="w-4 h-4" />
              Editar cliente
            </button>
            <button
              onClick={handleDelete}
              className="flex-1 flex items-center justify-center gap-2 px-4 py-2.5 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors font-medium"
            >
              <Trash2 className="w-4 h-4" />
              Eliminar cliente
            </button>
          </div>
        </div>
      </div>

      {/* Modal de Formulario de Receta */}
      {showPrescriptionForm && (
        <PrescriptionForm
          client={client}
          onClose={() => {
            setShowPrescriptionForm(false);
            setPrescriptionToEdit(undefined); 
          }}
          onSuccess={handlePrescriptionSuccess}
          prescriptionToEdit={prescriptionToEdit}

        />
      )}
    </>
  );
};

export default ClientDetailPanel;