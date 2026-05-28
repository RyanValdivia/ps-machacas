
import React, { useState, useEffect } from 'react';
import Modal from '../../../../components/Modal/modal';
import FormInput from '../../../../components/Forms/FormInput';
import type { Supplier, DEPARTAMENTO_CHOICES} from '../../../../types/supplier';
import Swal from 'sweetalert2';


interface ProveedorFormProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (proveedor: Supplier) => Promise<void>;
  proveedor?: Supplier | null;
  mode: 'create' | 'edit';
}

interface FormErrors {
  provRuc?: string;
  provRazSocial?: string;
  provDirec?: string;
  provTele?: string;
  provEmail?: string;
  provCiu?: string;
}
const DEPARTAMENTOS: { value: DEPARTAMENTO_CHOICES; label: string }[] = [
    { value: 'AMAZONAS', label: 'Amazonas' },
    { value: 'ANCASH', label: 'Áncash' },
    { value: 'APURIMAC', label: 'Apurímac' },
    { value: 'AREQUIPA', label: 'Arequipa' },
    { value: 'AYACUCHO', label: 'Ayacucho' },
    { value: 'CAJAMARCA', label: 'Cajamarca' },
    { value: 'CALLAO', label: 'Callao' },
    { value: 'CUSCO', label: 'Cusco' },
    { value: 'HUANCAVELICA', label: 'Huancavelica' },
    { value: 'HUANUCO', label: 'Huánuco' },
    { value: 'ICA', label: 'Ica' },
    { value: 'JUNIN', label: 'Junín' },
    { value: 'LA_LIBERTAD', label: 'La Libertad' },
    { value: 'LAMBAYEQUE', label: 'Lambayeque' },
    { value: 'LIMA', label: 'Lima' },
    { value: 'LORETO', label: 'Loreto' },
    { value: 'MADRE_DE_DIOS', label: 'Madre de Dios' },
    { value: 'MOQUEGUA', label: 'Moquegua' },
    { value: 'PASCO', label: 'Pasco' },
    { value: 'PIURA', label: 'Piura' },
    { value: 'PUNO', label: 'Puno' },
    { value: 'SAN_MARTIN', label: 'San Martín' },
    { value: 'TACNA', label: 'Tacna' },
    { value: 'TUMBES', label: 'Tumbes' },
    { value: 'UCAYALI', label: 'Ucayali' }
  ];

const ProveedorForm: React.FC<ProveedorFormProps> = ({
  isOpen,
  onClose,
  onSubmit,
  proveedor,
  mode
}) => {
    const initialState: Supplier = {
      provRuc: '',
      provRazSocial: '',
      provDirec: '',
      provTele: '',
      provEmail: '',
      provCiu: 'AREQUIPA',
      provEstado: 'Active'
    };
    const [formData, setFormData] = useState<Supplier>(initialState);
    const [errors, setErrors] = useState<FormErrors>({});
    const [isSubmitting, setIsSubmitting] = useState(false);
    const [backendError, setBackendError] = useState<string | null>(null);

    useEffect(() => {
        if (proveedor && mode === 'edit') {
          // Normalizar los valores null a cadenas vacías para el formulario
          setFormData({
            ...proveedor,
            provRuc: proveedor.provRuc || '',
            provDirec: proveedor.provDirec || '',
            provTele: proveedor.provTele || '',
            provEmail: proveedor.provEmail || '',
            provCiu: proveedor.provCiu || 'AREQUIPA',
          });
        } else {
          setFormData(initialState);
        }
        setErrors({});
        setBackendError(null);
    }, [proveedor, mode, isOpen]);

    const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
        const { name, value } = e.target;
        setFormData(prev => ({
        ...prev,
        [name]: value
        }));
        
        // Limpiar error del campo cuando el usuario escribe
        if (errors[name as keyof FormErrors]) {
        setErrors(prev => ({
            ...prev,
            [name]: undefined
        }));
        }
    };

    const validate = (): boolean => {
      const newErrors: FormErrors = {};

      // Validar Razón Social (OBLIGATORIO)
      if (!formData.provRazSocial || !formData.provRazSocial.trim()) {
        newErrors.provRazSocial = 'La razón social es obligatoria';
      } else if (formData.provRazSocial.length < 3) {
        newErrors.provRazSocial = 'La razón social debe tener al menos 3 caracteres';
      }

      // Validar RUC (OPCIONAL, pero si se llena debe ser válido)
      if (formData.provRuc && formData.provRuc.trim() && !/^\d{11}$/.test(formData.provRuc)) {
        newErrors.provRuc = 'El RUC debe tener 11 dígitos';
      }

      // Validar Teléfono (OPCIONAL, pero si se llena debe ser válido)
      if (formData.provTele && formData.provTele.trim() && !/^\d{9}$/.test(formData.provTele)) {
        newErrors.provTele = 'El teléfono debe tener 9 dígitos';
      }

      // Validar Email (OPCIONAL, pero si se llena debe ser válido)
      if (formData.provEmail && formData.provEmail.trim() && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.provEmail)) {
        newErrors.provEmail = 'El email no es válido';
      }

      setErrors(newErrors);
      return Object.keys(newErrors).length === 0;
    };
    
    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        
        if (!validate()) return;
        setIsSubmitting(true);
        setBackendError(null);
        
        try {
          await onSubmit(formData);
          handleClose();
          
          // Notificación de éxito con SweetAlert2
          Swal.fire({
            icon: 'success',
            title: mode === 'create' ? '¡Proveedor Creado!' : '¡Proveedor Actualizado!',
            text: mode === 'create' 
              ? 'El proveedor se ha creado exitosamente' 
              : 'El proveedor se ha actualizado exitosamente',
            timer: 2000,
            showConfirmButton: false
          });
        } catch (error: any) {
          console.error('Error al guardar:', error);
          
          // Manejar errores del backend
          if (error.provRuc) {
            setErrors(prev => ({ ...prev, provRuc: error.provRuc[0] }));
          }
          if (error.provTele) {
            setErrors(prev => ({ ...prev, provTele: error.provTele[0] }));
          }
          if (error.provEmail) {
            setErrors(prev => ({ ...prev, provEmail: error.provEmail[0] }));
          }
          if (error.provRazSocial) {
            setErrors(prev => ({ ...prev, provRazSocial: error.provRazSocial[0] }));
          }

          // Notificación de error con SweetAlert2
          Swal.fire({
            icon: 'error',
            title: 'Error',
            text: 'Error al guardar el proveedor. Por favor, verifica los datos.',
          });
          
          setBackendError('Error al guardar el proveedor. Por favor, verifica los datos.');
        } finally {
        setIsSubmitting(false);
        }
    };

    // Cerrar modal y limpiar formulario
    const handleClose = () => {
        setFormData(initialState);
        setErrors({});
        setBackendError(null);
        onClose();
    };

    return (
    <Modal
      isOpen={isOpen}
      onClose={handleClose}
      title={mode === 'create' ? 'Agregar Proveedor' : 'Editar Proveedor'}
      size="lg"
    >
      <form onSubmit={handleSubmit} className="space-y-4 sm:space-y-5 lg:space-y-6">
        {/* Mostrar error del backend si existe */}
        {backendError && (
          <div className="p-2 sm:p-3 lg:p-4 bg-red-100 border border-red-400 text-red-700 rounded-lg text-xs sm:text-sm lg:text-base">
            {backendError}
          </div>
        )}
        
        {/* Sección: Información Básica */}
        <div>
          <h3 className="text-sm sm:text-base lg:text-lg font-semibold text-gray-800 mb-2 sm:mb-3 lg:mb-4 pb-2 border-b border-gray-200">
            Información Básica
          </h3>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 sm:gap-4 lg:gap-6">
            {/* Razón Social */}
            <FormInput
              label="Razón Social"
              name="provRazSocial"
              type="text"
              value={formData.provRazSocial || ''}
              onChange={handleChange}
              error={errors.provRazSocial}
              required
              placeholder="Distribuidora Médica SAC"
            />
            
            {/* RUC */}
            <FormInput
              label="RUC"
              name="provRuc"
              type="text"
              value={formData.provRuc || ''}
              onChange={handleChange}
              error={errors.provRuc}
              placeholder="20567890123 (Opcional)"
              maxLength={11}
            />
          </div>
        </div>

        {/* Sección: Información de Contacto */}
        <div>
          <h3 className="text-sm sm:text-base lg:text-lg font-semibold text-gray-800 mb-2 sm:mb-3 lg:mb-4 pb-2 border-b border-gray-200">
            Información de Contacto
          </h3>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 sm:gap-4 lg:gap-6">
            {/* Teléfono */}
            <FormInput
              label="Teléfono"
              name="provTele"
              type="tel"
              value={formData.provTele || ''}
              onChange={handleChange}
              error={errors.provTele}
              placeholder="987654321 (Opcional)"
              maxLength={9}
            />

            {/* Email */}
            <FormInput
              label="Email"
              name="provEmail"
              type="email"
              value={formData.provEmail || ''}
              onChange={handleChange}
              error={errors.provEmail}
              placeholder="contacto@empresa.com (Opcional)"
            />
          </div>
        </div>

        {/* Sección: Ubicación y Estado */}
        <div>
          <h3 className="text-sm sm:text-base lg:text-lg font-semibold text-gray-800 mb-2 sm:mb-3 lg:mb-4 pb-2 border-b border-gray-200">
            Ubicación y Estado
          </h3>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 sm:gap-4 lg:gap-6">
            {/* Dirección */}
            <div className="sm:col-span-2">
              <FormInput
                label="Dirección"
                name="provDirec"
                type="text"
                value={formData.provDirec || ''}
                onChange={handleChange}
                error={errors.provDirec}
                placeholder="Av. Principal 123, Lima (Opcional)"
              />
            </div>

            {/* Ciudad */}
            <FormInput
              label="Ciudad/Departamento"
              name="provCiu"
              type="select"  
              value={formData.provCiu || 'AREQUIPA'}
              onChange={handleChange}
              error={errors.provCiu}
              options={DEPARTAMENTOS} 
              placeholder="Arequipa (Opcional)"
            />

            {/* Estado */}
            <div>
              <label 
                htmlFor="provEstado" 
                className="block text-xs sm:text-sm lg:text-base font-medium text-gray-700 mb-1 sm:mb-2"
              >
                Estado <span className="text-red-500">*</span>
              </label>
              <select
                id="provEstado"
                name="provEstado"
                value={formData.provEstado}
                onChange={handleChange}
                className="w-full px-3 sm:px-4 py-2 sm:py-2.5 lg:py-3 text-xs sm:text-sm lg:text-base border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition-colors"
              >
                <option value="Active">Activo</option>
                <option value="Inactive">Inactivo</option>
              </select>
            </div>
          </div>
        </div>

        {/* Botones de acción */}
        <div className="flex flex-col sm:flex-row justify-end gap-2 sm:gap-3 lg:gap-4 pt-4 sm:pt-5 lg:pt-6 border-t border-gray-200">
          <button
            type="button"
            onClick={handleClose}
            className="px-4 sm:px-6 lg:px-8 py-2 sm:py-2.5 lg:py-3 text-xs sm:text-sm lg:text-base border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 transition-colors font-medium"
            disabled={isSubmitting}
          >
            Cancelar
          </button>
          <button
            type="submit"
            className="px-4 sm:px-6 lg:px-8 py-2 sm:py-2.5 lg:py-3 text-xs sm:text-sm lg:text-base bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors disabled:bg-blue-300 disabled:cursor-not-allowed font-medium shadow-sm hover:shadow-md"
            disabled={isSubmitting}
          >
            {isSubmitting ? 'Guardando...' : mode === 'create' ? 'Agregar' : 'Guardar Cambios'}
          </button>
        </div>
      </form>
    </Modal>
  );

};
export default ProveedorForm;
