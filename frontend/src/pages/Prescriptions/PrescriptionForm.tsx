import { useState, useEffect } from "react";
import { Save, Plus, X, Trash2} from "lucide-react";
import type { Client } from "../../types/client";
import type { Prescription } from "../../types/prescription";
import type { Optometrist } from "../../auth/types/optometrist/optometrist";
import { createRecipe, updateRecipe, deleteRecipe } from "../../services/prescriptionService";
import api from "../../auth/services/api";
import { showSuccessToast, showErrorToast, showWarningToast, showDeleteConfirmation } from "../../utils/sweetAlertConfig";

type Props = {
  client: Client;
  prescriptionToEdit?: Prescription; // Nueva prop opcional para edición
  onClose?: () => void;
  onSuccess?: () => void;
};

const PrescriptionForm = ({ client, prescriptionToEdit, onClose, onSuccess }: Props) => {
  const [optometrists, setOptometrists] = useState<Optometrist[]>([]);
  const [showNewOptometristInput, setShowNewOptometristInput] = useState(false);
  const [newOptometristName, setNewOptometristName] = useState("");
  const [newOptometristLastName, setNewOptometristLastName] = useState("");

  const today = new Date().toISOString().split('T')[0];
  const isEditMode = !!prescriptionToEdit;

  const [formData, setFormData] = useState({
    recFech: prescriptionToEdit?.recFech || today,
    recEstado: (prescriptionToEdit?.recEstado || 'Activo') as 'Activo' | 'Inactivo',
    receEsfeOD: prescriptionToEdit?.receEsfeOD?.toString() || '',
    receCilinOD: prescriptionToEdit?.receCilinOD?.toString() || '',
    receEjeOD: prescriptionToEdit?.receEjeOD?.toString() || '',
    receAvccOD: prescriptionToEdit?.receAvccOD?.toString() || '',
    receEsfeOI: prescriptionToEdit?.receEsfeOI?.toString() || '',
    receCilinOI: prescriptionToEdit?.receCilinOI?.toString() || '',
    receEjeOI: prescriptionToEdit?.receEjeOI?.toString() || '',
    receAvccOI: prescriptionToEdit?.receAvccOI?.toString() || '',
    receAdd: prescriptionToEdit?.receAdd?.toString() || '',
    receDIP: prescriptionToEdit?.receDIP?.toString() || '',
    receDIPCerca: prescriptionToEdit?.receDIPCerca?.toString() || '',
    receEsExterna: prescriptionToEdit?.receEsExterna || false,
    recObservaciones: prescriptionToEdit?.recObservaciones || '',
    recInfoExtra: prescriptionToEdit?.recInfoExtra || '',
    diagnostico: prescriptionToEdit?.diagnostico || [] as string[],
    optCod: prescriptionToEdit?.optCod?.toString() || '',
  });

  useEffect(() => {
    loadOptometrists();
  }, []);

  const loadOptometrists = async () => {
    try {
      const res = await api.get('/clients/optometrist/');
      setOptometrists(res.data.data);
    } catch (error) {
      console.error("Error cargando optometristas:", error);
      showErrorToast("Error al cargar optometristas");
      setOptometrists([]);
    }
  };

  const handleCreateOptometrist = async () => {
    if (!newOptometristName.trim() || !newOptometristLastName.trim()) {
      showWarningToast("Ingrese nombre y apellido completos");
      return;
    }

    try {
      const res = await api.post('/clients/optometrist/', {
        optNombre: newOptometristName,
        optApellido: newOptometristLastName,
      });
      
      const newOpt = res.data.data || res.data;
      setOptometrists([...optometrists, newOpt]);
      setFormData({ ...formData, optCod: newOpt.optCod.toString() });
      setShowNewOptometristInput(false);
      setNewOptometristName("");
      setNewOptometristLastName("");
      showSuccessToast("Optometrista agregado exitosamente");
    } catch (error) {
      console.error("Error creando optometrista:", error);
      showErrorToast("Error al crear optometrista");
    }
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => {
    const { name, value, type } = e.target;
    
    if (type === 'checkbox') {
      const checked = (e.target as HTMLInputElement).checked;
      setFormData({ ...formData, [name]: checked });
    } else {
      setFormData({ ...formData, [name]: value });
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!formData.optCod) {
      showWarningToast("Seleccione un optometrista");
      return;
    }

    try {
      const dataToSend: Omit<Prescription, 'recCod'> = {
        recFech: formData.recFech,
        recEstado: formData.recEstado,
        receEsfeOD: formData.receEsfeOD ? parseFloat(formData.receEsfeOD) : null,
        receCilinOD: formData.receCilinOD ? parseFloat(formData.receCilinOD) : null,
        receEjeOD: formData.receEjeOD ? parseFloat(formData.receEjeOD) : null,
        receAvccOD: formData.receAvccOD ? parseFloat(formData.receAvccOD) : null,
        receEsfeOI: formData.receEsfeOI ? parseFloat(formData.receEsfeOI) : null,
        receCilinOI: formData.receCilinOI ? parseFloat(formData.receCilinOI) : null,
        receEjeOI: formData.receEjeOI ? parseFloat(formData.receEjeOI) : null,
        receAvccOI: formData.receAvccOI ? parseFloat(formData.receAvccOI) : null,
        receAdd: formData.receAdd ? parseFloat(formData.receAdd) : null,
        receDIP: formData.receDIP ? parseFloat(formData.receDIP) : null,
        receDIPCerca: formData.receDIPCerca ? parseFloat(formData.receDIPCerca) : null,
        receEsExterna: formData.receEsExterna,
        recObservaciones: formData.recObservaciones || null,
        recInfoExtra: formData.recInfoExtra || null,
        diagnostico: formData.diagnostico,
        cliCod: client.cliCod,
        optCod: parseInt(formData.optCod),
      };

      if (isEditMode && prescriptionToEdit) {
        await updateRecipe(prescriptionToEdit.recCod, dataToSend);
        showSuccessToast("Receta actualizada exitosamente");
      } else {
        await createRecipe(dataToSend);
        showSuccessToast("Receta creada exitosamente");
      }
      
      if (onSuccess) {
        onSuccess();
      }
      
      if (onClose) {
        onClose();
      }
    } catch (error: any) {
      console.error("Error guardando receta:", error);
      showErrorToast(isEditMode ? "Error al actualizar la receta" : "Error al guardar la receta");
    }
  };
  
  const handleDelete = async() => {
    if (!prescriptionToEdit) return;
    
    const result = await showDeleteConfirmation("esta receta");
    if (!result.isConfirmed) return;
    
    try {
      await deleteRecipe(prescriptionToEdit.recCod);
      showSuccessToast("Receta eliminada exitosamente");
      if (onSuccess) {
        onSuccess();
      }
      if (onClose) {
        onClose();
      }
    } catch (error: any) {
      console.error("Error eliminando receta:", error);
      showErrorToast("Error al eliminar la receta");
    }
  };

  const formContent = (
    <form onSubmit={handleSubmit} className="space-y-6">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Fecha <span className="text-red-500">*</span>
            </label>
            <input
              type="date"
              name="recFech"
              value={formData.recFech}
              onChange={handleInputChange}
              required
              className="w-full px-3 py-2 border border-gray-300 rounded-lg "
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Optometrista <span className="text-red-500">*</span>
            </label>
            <div className="flex gap-2">
              <select
                name="optCod"
                value={formData.optCod}
                onChange={handleInputChange}
                required
                className="flex-1 px-3 py-2 border border-gray-300 rounded-lg "
              >
                <option value="">Seleccionar...</option>
                {optometrists.map((opt) => (
                  <option key={opt.optCod} value={opt.optCod}>
                    {opt.optNombre} {opt.optApellido}
                  </option>
                ))}
              </select>
              <button
                type="button"
                onClick={() => setShowNewOptometristInput(!showNewOptometristInput)}
                className="px-3 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
                title="Agregar optometrista"
              >
                <Plus className="w-5 h-5" />
              </button>
            </div>
          </div>

        

        {showNewOptometristInput && (
          <div className="mt-4 p-4 bg-green-50 border border-green-200 rounded-lg">
            <h4 className="text-sm font-semibold text-gray-800 mb-3">Nuevo Optometrista</h4>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
              <input
                type="text"
                placeholder="Nombre"
                value={newOptometristName}
                onChange={(e) => setNewOptometristName(e.target.value)}
                className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-green-500"
              />
              <input
                type="text"
                placeholder="Apellido"
                value={newOptometristLastName}
                onChange={(e) => setNewOptometristLastName(e.target.value)}
                className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-green-500"
              />
              <button
                type="button"
                onClick={handleCreateOptometrist}
                className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors font-medium"
              >
                Guardar
              </button>
            </div>
          </div>
        )}
      </div>

      {/* Tabla de Receta */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
        
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-100">
              <tr>
                <th className=" py-1 text-left text-sm font-semibold text-gray-700 uppercase"></th>
                <th className=" py-1 text-center text-sm font-semibold text-gray-700 uppercase">SPH</th>
                <th className=" py-1 text-center text-sm font-semibold text-gray-700 uppercase">CYL</th>
                <th className=" py-1 text-center text-sm font-semibold text-gray-700 uppercase">Eje</th>
                <th className=" py-1 text-center text-sm font-semibold text-gray-700 uppercase">DIP</th>
                <th className=" py-1 text-center text-sm font-semibold text-gray-700 uppercase">AV.CC</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              <tr className="hover:bg-gray-50">
                <td className="px-4  font-medium text-gray-700">OD</td>
                <td className="">
                  <input
                    type="number"
                    step="0.25"
                    name="receEsfeOD"
                    value={formData.receEsfeOD}
                    onChange={handleInputChange}
                    placeholder="0.00"
                    className="w-full  py-2 border border-gray-300  text-center "
                  />
                </td>
                <td className=" ">
                  <input
                    type="number"
                    step="0.25"
                    name="receCilinOD"
                    value={formData.receCilinOD}
                    onChange={handleInputChange}
                    placeholder="0.00"
                    className="w-full py-2 border border-gray-300 text-center "
                  />
                </td>
                <td className=" ">
                  <input
                    type="number"
                    step="1"
                    name="receEjeOD"
                    value={formData.receEjeOD}
                    onChange={handleInputChange}
                    placeholder="0"
                    min="0"
                    max="180"
                    className="w-full  py-2 border border-gray-300 text-center "
                  />
                </td>
                <td className="" rowSpan={2}>
                  <input
                    type="number"
                    step="1"
                    name="receDIP"
                    value={formData.receDIP}
                    onChange={handleInputChange}
                    className="w-full py-7.5 border border-gray-300  text-center "
                  />
                </td>
                <td className="">
                  <input
                    type="number"
                    step="1"
                    name="receAvccOD"
                    value={formData.receAvccOD}
                    onChange={handleInputChange}
                    className="w-full py-2 border border-gray-300  text-center "
                  />
                </td>
              </tr>
              {/*Ojo Izquierdo*/}
              <tr className="hover:bg-gray-50">
                <td className="px-4  font-medium text-gray-700">OI</td>
                <td className="">
                  <input
                    type="number"
                    step="0.25"
                    name="receEsfeOI"
                    value={formData.receEsfeOI}
                    onChange={handleInputChange}
                    placeholder="0.00"
                    className="w-full py-2 border border-gray-300 text-center "
                  />
                </td>
                <td className="">
                  <input
                    type="number"
                    step="0.25"
                    name="receCilinOI"
                    value={formData.receCilinOI}
                    onChange={handleInputChange}
                    placeholder="0.00"
                    className="w-full py-2 border border-gray-300  text-center "
                  />
                </td>
                <td className="">
                  <input
                    type="number"
                    step="1"
                    name="receEjeOI"
                    value={formData.receEjeOI}
                    onChange={handleInputChange}
                    placeholder="0"
                    min="0"
                    max="180"
                    className="w-full  py-2 border border-gray-300  text-center "
                  />
                </td>
                <td className="">
                  <input
                    type="number"
                    step="1"
                    name="receAvccOI"
                    value={formData.receAvccOI}
                    onChange={handleInputChange}
                    className="w-full py-2 border border-gray-300 text-center "
                  />
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <div className="px-6 py-4 bg-green-50 border-t border-gray-200">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">ADD</label>
              <input
                type="number"
                step="0.25"
                name="receAdd"
                value={formData.receAdd}
                onChange={handleInputChange}
                placeholder="0.00"
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-yellow-500"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">DIP Cerca</label>
              <input
                type="number"
                step="0.5"
                name="receDIPCerca"
                value={formData.receDIPCerca}
                onChange={handleInputChange}
                placeholder="0.0"
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-yellow-500"
              />
            </div>
          </div>
        </div>
      </div>

      {/* Observaciones */}
      <div className="bg-white rounded-lg shadow-sm">
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Observaciones</label>
            <textarea
              name="recObservaciones"
              value={formData.recObservaciones}
              onChange={handleInputChange}
              rows={3}
              placeholder="Ingrese observaciones..."
              className="w-full px-3 py-2 border border-gray-300 rounded-lg "
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Información Extra</label>
            <textarea
              name="recInfoExtra"
              value={formData.recInfoExtra}
              onChange={handleInputChange}
              rows={3}
              placeholder="Ingrese información adicional..."
              className="w-full px-3 py-2 border border-gray-300 rounded-lg "
            />
          </div>
        </div>
      </div>

      {/* Botones: añadimos eliminar solo si es editar, no CREAR */} 
      <div className="flex gap-3 justify-end">
        {isEditMode && (
        <div>
          <button
            type="button"
            onClick={() => {
              handleDelete();
            }}
            
            className="px-6 py-2.5 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 transition-colors font-medium"
          >
          <Trash2 className="w-5 h-5 text-red-500" />
          </button>
        </div>
        )}
        <button
          type="button"
          onClick={() => {
            if (onClose) {
              onClose();
            }
          }}
          className="px-6 py-2.5 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 transition-colors font-medium"
        >
          Cancelar
        </button>
        <button
          type="submit"
          className="flex items-center gap-2 px-6 py-2.5 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium shadow-sm"
        >
          <Save className="w-5 h-5" />
          {isEditMode ? 'Actualizar Receta' : 'Guardar Receta'}
        </button>
      </div>
    </form>
  );

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      <div 
        className="absolute inset-0 bg-black/50 backdrop-blur-sm"
        onClick={onClose}
      />
      
      <div className="relative bg-white rounded-xl shadow-2xl w-full max-w-xl max-h-[90vh] overflow-hidden z-10">
        <div className="sticky top-0 bg-white border-b border-gray-200 px-6 py-4 flex items-center justify-between">
          <div>
            <h3 className="text-xl font-bold text-gray-800">
              {isEditMode ? 'Editar Receta' : 'Nueva Receta'}
            </h3>
            <p className="text-sm text-gray-600 mt-1">
              Paciente: <span className="font-semibold">{client.cliNomCompleto}</span>
            </p>
            
          </div>
          <div className="flex items-center gap-4">
            <label className="flex items-center gap-2 text-sm text-gray-700">
              <input
                type="checkbox"
                name="receEsExterna"
                checked={formData.receEsExterna}
                onChange={handleInputChange}
                className="w-4 h-4 text-blue-600 border-gray-300 rounded"
              />
              <span className="font-semibold ">Trajo su receta</span>
            </label>

            <button
              onClick={onClose}
              className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
            >
              <X className="w-6 h-6 text-gray-600" />
            </button>
          </div>
        </div>
        
        <div className="overflow-y-auto max-h-[calc(90vh-80px)] px-6 py-6">
          {formContent}
        </div>
      </div>
    </div>
  );
};

export default PrescriptionForm;