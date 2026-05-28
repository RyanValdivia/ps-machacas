import React, { useState, useEffect } from 'react';
import { Upload, Building2, Save, X } from 'lucide-react';
import FormInput from '../../../../components/Forms/FormInput';
import { getOpticalCenter, updateOpticalCenter, createOpticalCenter } from '../../../../services/opticalConfigService';
import type { OpticalCenter } from '../../../../types/opticalCenter';

interface InfoFormProps {
    onSuccess?: () => void;
}

const InfoForm: React.FC<InfoFormProps> = ({ onSuccess }) => {
    const [formData, setFormData] = useState<OpticalCenter>({
        optNom: '',
        optLema: '',
        optDir: '',
        optProv: '',
        optTel: '',
        optLogo: null,
        optLogoUrl: null // Para la URL base64 del servidor
    });

    const [logoPreview, setLogoPreview] = useState<string | null>(null);
    const [logoFile, setLogoFile] = useState<File | null>(null);
    const [isEditMode, setIsEditMode] = useState(false);
    const [isLoading, setIsLoading] = useState(true);
    const [isSaving, setIsSaving] = useState(false);
    const [errors, setErrors] = useState<Record<string, string>>({});
    const [successMessage, setSuccessMessage] = useState<string>('');

    // Cargar datos existentes al montar el componente
    useEffect(() => {
        console.log('🔄 [DEBUG] useEffect: Componente montado, cargando datos...');
        loadOpticalCenter();
    }, []);

    const loadOpticalCenter = async () => {
        console.log('📥 [DEBUG] loadOpticalCenter: Iniciando carga de datos');
        try {
            setIsLoading(true);
            const data = await getOpticalCenter();
            console.log('✅ [DEBUG] loadOpticalCenter: Datos recibidos:', data);
            
            if (data && data.optNom) {
                console.log('✅ [DEBUG] Datos válidos encontrados. Modo: EDICIÓN');
                setFormData(data);
                setIsEditMode(true);
                
                // CAMBIO IMPORTANTE: Usar optLogoUrl en lugar de optLogo
                if (data.optLogoUrl) {
                    console.log('🖼️ [DEBUG] Logo URL encontrado (base64):', data.optLogoUrl.substring(0, 100) + '...');
                    setLogoPreview(data.optLogoUrl);
                } else {
                    console.log('ℹ️ [DEBUG] No hay logo en los datos');
                }
            } else {
                console.log('ℹ️ [DEBUG] No hay datos previos. Modo: CREACIÓN');
                setIsEditMode(false);
            }
        } catch (error) {
            console.error('⚠️ [DEBUG] loadOpticalCenter: Error al cargar:', error);
            console.log('📝 [DEBUG] Entrando en modo creación por error');
            setIsEditMode(false);
        } finally {
            setIsLoading(false);
            console.log('🏁 [DEBUG] loadOpticalCenter: Carga finalizada');
        }
    };

    const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
        const { name, value } = e.target;
        setFormData(prev => ({
            ...prev,
            [name]: value
        }));
        
        // Validación en tiempo real
        const newErrors = { ...errors };
        
        switch (name) {
            case 'optNom':
                if (!value.trim()) {
                    newErrors.optNom = 'El nombre de la óptica es obligatorio';
                } else if (value.trim().length < 3) {
                    newErrors.optNom = 'El nombre debe tener al menos 3 caracteres';
                } else if (value.length > 100) {
                    newErrors.optNom = 'El nombre no debe superar los 100 caracteres';
                } else {
                    delete newErrors.optNom;
                }
                break;
                
            case 'optLema':
                if (value.length > 200) {
                    newErrors.optLema = 'El lema no debe superar los 200 caracteres';
                } else {
                    delete newErrors.optLema;
                }
                break;
                
            case 'optDir':
                if (value.length > 200) {
                    newErrors.optDir = 'La dirección no debe superar los 200 caracteres';
                } else {
                    delete newErrors.optDir;
                }
                break;
                
            case 'optProv':
                if (value.length > 100) {
                    newErrors.optProv = 'La provincia no debe superar los 100 caracteres';
                } else {
                    delete newErrors.optProv;
                }
                break;
                
            case 'optTel':
                if (value.trim()) {
                    const telRegex = /^[\d\s\-\+\(\)]+$/;
                    if (!telRegex.test(value.trim())) {
                        newErrors.optTel = ' Solo números y caracteres válidos (+, -, espacio, paréntesis)';
                    } else if (value.trim().replace(/[\s\-\+\(\)]/g, '').length < 7 && value.trim().replace(/[\s\-\+\(\)]/g, '').length > 0) {
                        newErrors.optTel = ' El teléfono debe tener al menos 7 dígitos';
                    } else if (value.length > 20) {
                        newErrors.optTel = ' El teléfono no debe superar los 20 caracteres';
                    } else {
                        delete newErrors.optTel;
                    }
                } else {
                    delete newErrors.optTel;
                }
                break;
                
            default:
                // Para otros campos, solo limpiar el error si existía
                if (newErrors[name]) {
                    delete newErrors[name];
                }
        }
        
        setErrors(newErrors);
    };

    const handleLogoChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        console.log('🖼️ [DEBUG] handleLogoChange: Evento disparado');
        const file = e.target.files?.[0];
        
        if (!file) {
            console.log('⚠️ [DEBUG] handleLogoChange: No se seleccionó ningún archivo');
            return;
        }
        
        console.log('📸 [DEBUG] Archivo seleccionado:', {
            name: file.name,
            size: file.size,
            type: file.type,
            lastModified: new Date(file.lastModified).toISOString()
        });
        
        // Limpiar errores previos
        setErrors(prev => {
            const newErrors = { ...prev };
            delete newErrors.optLogo;
            return newErrors;
        });

        // Validar tipo de archivo
        const validTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/webp'];
        if (!validTypes.includes(file.type)) {
            console.error('❌ [DEBUG] Tipo de archivo inválido:', file.type);
            setErrors(prev => ({
                ...prev,
                optLogo: ' Formato no válido. Use JPG, PNG, GIF o WEBP'
            }));
            e.target.value = ''; // Limpiar input
            return;
        }
        console.log('✅ [DEBUG] Tipo de archivo válido:', file.type);

        // Validar tamaño (máximo 5MB)
        const maxSize = 5 * 1024 * 1024; // 5MB
        if (file.size > maxSize) {
            const sizeMB = (file.size / (1024 * 1024)).toFixed(2);
            console.error('❌ [DEBUG] Archivo muy grande:', sizeMB, 'MB');
            setErrors(prev => ({
                ...prev,
                optLogo: `El archivo es muy grande (${sizeMB}MB). Máximo 5MB`
            }));
            e.target.value = ''; // Limpiar input
            return;
        }
        console.log('✅ [DEBUG] Tamaño de archivo válido:', (file.size / 1024).toFixed(2), 'KB');

        // Validar dimensiones mínimas
        console.log('🔍 [DEBUG] Iniciando lectura del archivo con FileReader...');
        const reader = new FileReader();
        reader.onload = (event) => {
            console.log('✅ [DEBUG] FileReader: Archivo leído exitosamente');
            const img = new Image();
            img.onload = () => {
                console.log('✅ [DEBUG] Imagen cargada. Dimensiones:', img.width, 'x', img.height);
                
                // Verificar dimensiones mínimas
                if (img.width < 50 || img.height < 50) {
                    console.error('❌ [DEBUG] Imagen muy pequeña:', img.width, 'x', img.height);
                    setErrors(prev => ({
                        ...prev,
                        optLogo: ' La imagen es muy pequeña. Mínimo 50x50 píxeles'
                    }));
                    e.target.value = '';
                    setLogoPreview(null);
                    setLogoFile(null);
                    return;
                }

                // Verificar dimensiones máximas (advertencia, no error)
                if (img.width > 2000 || img.height > 2000) {
                    console.warn('⚠️ [DEBUG] La imagen es muy grande. Se recomienda usar imágenes menores a 2000x2000px');
                }

                // Todo OK, guardar el archivo
                console.log('✅ [DEBUG] Imagen validada correctamente. Guardando en estado...');
                setLogoFile(file);
                // Usar la data URL para previsualización local
                setLogoPreview(event.target?.result as string);
                console.log('✅ [DEBUG] Estado actualizado. Logo listo para enviar.');
            };
            img.onerror = (error) => {
                console.error('❌ [DEBUG] Error al cargar la imagen:', error);
                setErrors(prev => ({
                    ...prev,
                    optLogo: ' Error al leer la imagen. Intente con otro archivo'
                }));
                e.target.value = '';
            };
            img.src = event.target?.result as string;
        };
        reader.onerror = (error) => {
            console.error('❌ [DEBUG] Error en FileReader:', error);
            setErrors(prev => ({
                ...prev,
                optLogo: ' Error al procesar el archivo'
            }));
            e.target.value = '';
        };
        reader.readAsDataURL(file);
    };

    const handleRemoveLogo = () => {
        setLogoFile(null);
        setLogoPreview(null);
        setFormData(prev => ({
            ...prev,
            optLogo: null,
            optLogoUrl: null
        }));
    };

    const validateForm = (): boolean => {
        const newErrors: Record<string, string> = {};

        // Validar nombre (obligatorio)
        if (!formData.optNom || formData.optNom.trim() === '') {
            newErrors.optNom = 'El nombre de la óptica es obligatorio';
        } else if (formData.optNom.trim().length < 3) {
            newErrors.optNom = 'El nombre debe tener al menos 3 caracteres';
        } else if (formData.optNom.length > 100) {
            newErrors.optNom = 'El nombre no debe superar los 100 caracteres';
        }

        // Validar lema (opcional pero con límite)
        if (formData.optLema && formData.optLema.length > 200) {
            newErrors.optLema = 'El lema no debe superar los 200 caracteres';
        }

        // Validar dirección (opcional pero con límite)
        if (formData.optDir && formData.optDir.length > 200) {
            newErrors.optDir = 'La dirección no debe superar los 200 caracteres';
        }

        // Validar provincia (opcional pero con límite)
        if (formData.optProv && formData.optProv.length > 100) {
            newErrors.optProv = 'La provincia no debe superar los 100 caracteres';
        }

        // Validar teléfono (opcional pero con formato)
        if (formData.optTel) {
            const telClean = formData.optTel.trim();
            if (telClean.length > 0) {
                // Validar que solo contenga números, espacios, guiones, paréntesis y +
                const telRegex = /^[\d\s\-\+\(\)]+$/;
                if (!telRegex.test(telClean)) {
                    newErrors.optTel = 'El teléfono solo debe contener números y caracteres válidos (+, -, espacio, paréntesis)';
                } else if (telClean.replace(/[\s\-\+\(\)]/g, '').length < 7) {
                    newErrors.optTel = 'El teléfono debe tener al menos 7 dígitos';
                } else if (telClean.length > 20) {
                    newErrors.optTel = 'El teléfono no debe superar los 20 caracteres';
                }
            }
        }

        console.log('Errores de validación:', newErrors);
        setErrors(newErrors);
        return Object.keys(newErrors).length === 0;
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        console.log('📝 [DEBUG] handleSubmit: Formulario enviado');

        if (!validateForm()) {
            console.log('❌ [DEBUG] Validación fallida. Errores:', errors);
            // Scroll al primer error
            const firstErrorField = document.querySelector('.border-red-300');
            if (firstErrorField) {
                firstErrorField.scrollIntoView({ behavior: 'smooth', block: 'center' });
            }
            return;
        }
        
        console.log('✅ [DEBUG] Validación exitosa. Preparando datos para enviar...');

        setIsSaving(true);
        setSuccessMessage('');
        setErrors({});

        try {
            // Crear FormData para enviar con el logo
            const submitData = new FormData();

            console.log('📦 [DEBUG] Agregando datos al FormData...');
            submitData.append('optNom', formData.optNom.trim());
            submitData.append('optLema', formData.optLema?.trim() || '');
            submitData.append('optDir', formData.optDir?.trim() || '');
            submitData.append('optProv', formData.optProv?.trim() || '');
            submitData.append('optTel', formData.optTel?.trim() || '');

            if (logoFile) {
                console.log('📸 [DEBUG] Agregando archivo de logo al FormData:', {
                    name: logoFile.name,
                    size: logoFile.size,
                    type: logoFile.type
                });
                submitData.append('optLogo', logoFile);
            } else {
                console.log('ℹ️ [DEBUG] No hay archivo de logo para enviar');
            }
            
            console.log('📤 [DEBUG] Datos preparados. Modo:', isEditMode ? 'Edición' : 'Creación');

            let response;
            if (isEditMode) {
                console.log('🔄 [DEBUG] Llamando a updateOpticalCenter...');
                response = await updateOpticalCenter(submitData as any);
                console.log('✅ [DEBUG] Respuesta de updateOpticalCenter:', response);
                setSuccessMessage('Los datos de la óptica fueron actualizados correctamente');
            } else {
                console.log('➕ [DEBUG] Llamando a createOpticalCenter...');
                response = await createOpticalCenter(submitData as any);
                console.log('✅ [DEBUG] Respuesta de createOpticalCenter:', response);
                setSuccessMessage('Los datos de la óptica fueron creados correctamente');
                setIsEditMode(true);
            }

            console.log('📥 [DEBUG] Actualizando estado con respuesta del servidor...');
            setFormData(response);
            
            // CAMBIO IMPORTANTE: Usar optLogoUrl en lugar de optLogo
            if (response.optLogoUrl) {
                console.log('🖼️ [DEBUG] Logo URL en respuesta:', response.optLogoUrl.substring(0, 100) + '...');
                setLogoPreview(response.optLogoUrl);
            } else {
                console.log('⚠️ [DEBUG] No hay logo en la respuesta del servidor');
            }
            setLogoFile(null);

            if (onSuccess) {
                console.log('✅ [DEBUG] Llamando callback onSuccess');
                onSuccess();
            }

            // Scroll al mensaje de éxito
            window.scrollTo({ top: 0, behavior: 'smooth' });

            // Limpiar mensaje después de 5 segundos
            setTimeout(() => {
                setSuccessMessage('');
            }, 5000);

        } catch (error: any) {
            console.error('❌ [DEBUG] Error saving optical center:', error);
            console.error('❌ [DEBUG] Error completo:', {
                message: error.message,
                response: error.response?.data,
                status: error.response?.status,
                statusText: error.response?.statusText
            });
            
            // Procesar errores del backend
            let errorMessage = 'Error al guardar los datos. Por favor intente nuevamente.';
            const backendErrors: Record<string, string> = {};
            
            if (error.response?.data) {
                const errorData = error.response.data;
                console.log('📋 [DEBUG] Datos del error del backend:', errorData);
                
                // Si el backend devuelve un objeto con errores por campo
                if (typeof errorData === 'object') {
                    Object.keys(errorData).forEach(key => {
                        const fieldError = errorData[key];
                        const errorText = Array.isArray(fieldError) ? fieldError[0] : fieldError;
                        
                        console.log(`🔍 [DEBUG] Error en campo "${key}":`, errorText);
                        
                        // Mapear nombres de campos del backend al frontend
                        const fieldMap: Record<string, string> = {
                            'optNom': 'optNom',
                            'optLema': 'optLema',
                            'optDir': 'optDir',
                            'optProv': 'optProv',
                            'optTel': 'optTel',
                            'optLogo': 'optLogo'
                        };
                        
                        const frontendField = fieldMap[key] || key;
                        backendErrors[frontendField] = errorText;
                    });
                } else if (typeof errorData === 'string') {
                    console.log('📋 [DEBUG] Error como string:', errorData);
                    errorMessage = errorData;
                } else if (errorData.message) {
                    console.log('📋 [DEBUG] Error message:', errorData.message);
                    errorMessage = errorData.message;
                }
            }
            
            // Si hay errores de campos específicos, mostrarlos
            if (Object.keys(backendErrors).length > 0) {
                console.log('📋 [DEBUG] Errores de campos específicos:', backendErrors);
                setErrors(backendErrors);
                // Scroll al primer error
                setTimeout(() => {
                    const firstErrorField = document.querySelector('.border-red-300');
                    if (firstErrorField) {
                        firstErrorField.scrollIntoView({ behavior: 'smooth', block: 'center' });
                    }
                }, 100);
            } else {
                // Error general
                console.log('📋 [DEBUG] Error general:', errorMessage);
                setErrors({
                    submit: errorMessage
                });
                window.scrollTo({ top: 0, behavior: 'smooth' });
            }
        } finally {
            console.log('🏁 [DEBUG] Finalizando guardado. isSaving = false');
            setIsSaving(false);
        }
    };

    if (isLoading) {
        return (
            <div className="flex items-center justify-center py-12">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
            </div>
        );
    }

    return (
        <div className="p-3 sm:p-4 max-w-7xl mx-auto">
            <form onSubmit={handleSubmit} className="space-y-4">
                {/* Header con modo */}
                <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 mb-4">
                    <div className="flex items-center gap-2">
                        <Building2 className="w-6 h-6 text-blue-600" />
                        <div>
                            <h2 className="text-lg sm:text-xl font-bold text-gray-800">
                                {isEditMode ? 'Editar Información de la Óptica' : 'Datos de la Óptica'}
                            </h2>
                            <p className="text-xs sm:text-sm text-gray-500 mt-0.5">
                                {isEditMode ? 'Actualice los datos de su negocio' : 'Configure los datos de su negocio'}
                            </p>
                        </div>
                    </div>
                </div>

                {/* Mensajes de éxito/error */}
                {successMessage && (
                    <div className="bg-green-50 border-l-4 border-green-400 px-3 py-2 rounded-r text-xs sm:text-sm flex items-center gap-2">
                        <svg className="w-5 h-5 text-green-600 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                            <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                        </svg>
                        <p className="font-medium text-green-800">{successMessage}</p>
                    </div>
                )}

                {errors.submit && (
                    <div className="bg-red-50 border-l-4 border-red-400 px-3 py-2 rounded-r text-xs sm:text-sm flex items-start gap-2">
                        <svg className="w-5 h-5 text-red-600 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                            <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                        </svg>
                        <div>
                            <p className="font-medium text-red-800">Error al guardar</p>
                            <p className="text-xs text-red-700 mt-0.5">{errors.submit}</p>
                        </div>
                    </div>
                )}

                {/* Información de campos requeridos */}
                {!isEditMode && (
                    <div className="bg-blue-50 border-l-4 border-blue-400 px-3 py-2 rounded-r text-xs sm:text-sm flex items-start gap-2">
                        <svg className="w-4 h-4 text-blue-600 flex-shrink-0 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
                            <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
                        </svg>
                        <div className="text-blue-800">
                            <p className="font-medium">Configure los datos de su óptica</p>
                            <p className="mt-0.5">Los campos marcados con <span className="text-red-500">*</span> son obligatorios</p>
                        </div>
                    </div>
                )}

                {/* Contenedor principal con dos columnas */}
                <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                    {/* Columna de formulario */}
                    <div className="lg:col-span-2 space-y-4">
                        <FormInput
                            label="Nombre de la Óptica"
                            name="optNom"
                            value={formData.optNom}
                            onChange={handleInputChange}
                            error={errors.optNom}
                            required
                            placeholder="Ej: Óptica Central"
                            maxLength={100}
                            showSuccess={true}
                        />

                        <FormInput
                            label="Lema o Slogan"
                            name="optLema"
                            value={formData.optLema || ''}
                            onChange={handleInputChange}
                            error={errors.optLema}
                            placeholder="Ej: Tu visión, nuestro compromiso"
                            maxLength={200}
                        />

                        <FormInput
                            label="Dirección"
                            name="optDir"
                            value={formData.optDir || ''}
                            onChange={handleInputChange}
                            error={errors.optDir}
                            placeholder="Ej: Calle. Principal 123"
                            maxLength={200}
                        />

                        <FormInput
                            label="Provincia/Ciudad"
                            name="optProv"
                            value={formData.optProv || ''}
                            onChange={handleInputChange}
                            error={errors.optProv}
                            placeholder="Ej: Arequipa"
                            maxLength={100}
                        />

                        <FormInput
                            label="Teléfono"
                            name="optTel"
                            type="tel"
                            value={formData.optTel || ''}
                            onChange={handleInputChange}
                            error={errors.optTel}
                            placeholder="Ej: 999 999 999"
                            maxLength={20}
                            showSuccess={true}
                        />
                    </div>

                    {/* Columna de logo */}
                    <div className="lg:col-span-1">
                        <div className="sticky top-4">
                            <label className="block text-sm font-medium text-gray-700 mb-2">
                                Logo de la Óptica
                            </label>

                            {/* Preview del logo */}
                            <div className="mb-4">
                                <div className="relative w-full aspect-square bg-gradient-to-br from-gray-50 to-gray-100 rounded-xl border-2 border-dashed border-gray-300 overflow-hidden">
                                    {logoPreview ? (
                                        <>
                                            <img
                                                src={logoPreview}
                                                alt="Logo preview"
                                                className="w-full h-full object-contain p-4"
                                            />
                                            <button
                                                type="button"
                                                onClick={handleRemoveLogo}
                                                className="absolute top-2 right-2 bg-red-500 hover:bg-red-600 text-white p-2 rounded-full shadow-lg transition-colors"
                                                title="Eliminar logo"
                                            >
                                                <X className="w-4 h-4" />
                                            </button>
                                        </>
                                    ) : (
                                        <div className="absolute inset-0 flex flex-col items-center justify-center text-gray-400">
                                            <Building2 className="w-16 h-16 mb-2" />
                                            <p className="text-sm font-medium">Sin logo</p>
                                        </div>
                                    )}
                                </div>
                            </div>

                            {/* Input para subir logo */}
                            <div className="space-y-2">
                                <label
                                    htmlFor="logo-upload"
                                    className="flex items-center justify-center gap-2 px-4 py-3 bg-blue-600 hover:bg-blue-700 text-white rounded-lg cursor-pointer transition-colors shadow-sm"
                                >
                                    <Upload className="w-5 h-5" />
                                    <span className="font-medium">
                                        {logoPreview ? 'Cambiar Logo' : 'Subir Logo'}
                                    </span>
                                </label>
                                <input
                                    id="logo-upload"
                                    type="file"
                                    accept="image/*"
                                    onChange={handleLogoChange}
                                    className="hidden"
                                />

                                <p className="text-xs text-gray-500 text-center">
                                    JPG, PNG, GIF, WEBP • Máx. 5MB • Mín. 50x50px
                                </p>

                                {errors.optLogo && (
                                    <div className="bg-red-50 border border-red-200 text-red-700 px-3 py-2 rounded text-xs text-center">
                                        {errors.optLogo}
                                    </div>
                                )}
                                
                                {!errors.optLogo && logoFile && (
                                    <div className="bg-green-50 border border-green-200 text-green-700 px-3 py-2 rounded text-xs text-center flex items-center justify-center gap-2">
                                        <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                                            <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                                        </svg>
                                        Logo listo para guardar
                                    </div>
                                )}
                            </div>
                        </div>
                    </div>
                </div>

                {/* Botón de guardar */}
                <div className="flex justify-end pt-6 border-t border-gray-200">
                    <button
                        type="submit"
                        disabled={isSaving}
                        className="flex items-center gap-2 px-6 py-3 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white rounded-lg font-medium transition-colors shadow-sm disabled:cursor-not-allowed"
                    >
                        {isSaving ? (
                            <>
                                <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                                <span>Guardando...</span>
                            </>
                        ) : (
                            <>
                                <Save className="w-5 h-5" />
                                <span>{isEditMode ? 'Actualizar Datos' : 'Guardar datos'}</span>
                            </>
                        )}
                    </button>
                </div>
            </form>
        </div>
    );
};

export default InfoForm;