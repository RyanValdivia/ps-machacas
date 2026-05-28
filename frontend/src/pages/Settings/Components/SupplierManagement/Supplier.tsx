// 🔹 Responsable: Denise
// Tareas:
// 1. Crear tabla con proveedores, en el trello ya esta para qeu te guies.
// 2. Agregar formulario CRUD (crear, editar, eliminar).
// 3. Integrar con el backend (/api/proveedores/).
// 4. Mostrar en Configuración junto con Sucursales.

import React, { useEffect, useState } from 'react';
import {  Plus, Edit2, Trash2,RefreshCw } from 'lucide-react';
import DataTable, { type Column } from "../../../../components/Table/DataTable";
import ProveedorForm from './SupplierForm';
import supplierService from '../../../../services/supplierService';
import type { Supplier } from '../../../../types/supplier';
import Swal from 'sweetalert2';

//Cambio: Nuevos componentes Commons
import AddButton from '../../../../components/Common/AddButton';
import SearchInput from '../../../../components/Common/SearchInput';
import RemoveButton from '../../../../components/Common/RemoveButton';
import ReloadButton from '../../../../components/Common/ReloadButton';

const SupplierPage: React.FC = () => {
  // Estado para almacenar los proveedores
  const [supplier, setSupplier] = useState<Supplier[]>([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [selectedProveedor, setSelectedProveedor] = useState<Supplier | null>(null);
  const [modalMode, setModalMode] = useState<'create' | 'edit'>('create');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [totalCount, setTotalCount] = useState(0);

  useEffect(() => {
    fetchProveedores();
  }, []);

  // Función para cargar proveedores desde el backend
  const fetchProveedores = async (search?: string) => {
    setLoading(true);
    setError(null);
    try {
      console.log('Fetching suppliers...');
      const data = await supplierService.getAll({
        search: search || undefined,
      });
      console.log('Suppliers loaded:', data);
      setSupplier(data);
      setTotalCount(data.length);
    } catch (err: any) {
      console.error('Error loading suppliers:', err);
      setError('Error al cargar los proveedores. Verifica que el backend esté corriendo.');
    } finally {
      setLoading(false);
    }
  };



  const normalizeText = (text: string) => text.normalize('NFD').toLowerCase();

  // Para filtrar proveedores según el término de búsqueda(segun razon social o ruc)
  const proveedoresFiltrados = supplier.filter(supplier =>
    normalizeText(supplier.provRazSocial).includes(normalizeText(searchTerm)) ||
    (supplier.provRuc && supplier.provRuc.includes(searchTerm))
  );

  // Abrir modal para crear
  const handleCreate = () => {
    setModalMode('create');
    setSelectedProveedor(null);
    setIsModalOpen(true);
  };

  // Abrir modal para editar
  const handleEdit = (supplier: Supplier) => {
    setModalMode('edit');
    setSelectedProveedor(supplier);
    setIsModalOpen(true);
  };

  // eliminar proveedor 
  const handleDelete = async (supplier: Supplier) => {
    const result = await Swal.fire({
      title: '¿Estás seguro?',
      text: `¿Deseas eliminar al proveedor "${supplier.provRazSocial}"?`,
      icon: 'warning',
      showCancelButton: true,
      confirmButtonColor: '#3085d6',
      cancelButtonColor: '#d33',
      confirmButtonText: 'Sí, eliminar',
      cancelButtonText: 'Cancelar'
    });

    if (result.isConfirmed) {
      try {
        await supplierService.delete(supplier.provCod!);
        await fetchProveedores(searchTerm);
        
        Swal.fire({
          icon: 'success',
          title: '¡Eliminado!',
          text: 'Proveedor eliminado exitosamente',
          timer: 2000,
          showConfirmButton: false
        });
      } catch (err: any) {
        console.error('Error al eliminar:', err);
        
        // Verificar si es un error de protección (productos asociados)
        if (err.response?.data?.error === 'protected_delete') {
          const productCount = err.response.data.product_count;
          Swal.fire({
            icon: 'error',
            title: 'No se puede eliminar',
            html: `
              <p>${err.response.data.message}</p>
              <p><strong>Productos asociados:</strong> ${productCount}</p>
              <p>${err.response.data.detail}</p>
            `,
          });
        } else {
          Swal.fire({
            icon: 'error',
            title: 'Error',
            text: 'Error al eliminar el proveedor. Intenta nuevamente.',
          });
        }
      }
    }
  };

  // guardar proveedor
  const handleSubmit = async (proveedor: Supplier) => {
    try {
      if (modalMode === 'create') {
        await supplierService.create(proveedor);
        console.log('Proveedor creado exitosamente');
      } else {
        await supplierService.update(proveedor.provCod!, proveedor);
        console.log('Proveedor actualizado exitosamente');
      }
      await fetchProveedores(searchTerm);
      setIsModalOpen(false);
    } catch (err: any) {
      console.error('Error al guardar:', err);
      throw err; 
    }
  };


  // Definir las columnas de la tabla
  const columns: Column<Supplier>[] = [
    {
      key: 'provCod',
      label: 'CÓDIGO',
      render: (row) => (
        <span className="text-gray-900 font-medium text-sm">{row.provCod}</span>
      )
    },
    {
      key: 'provRuc',
      label: 'RUC',
      render: (row) => (
        <span className="text-gray-700 text-sm">{row.provRuc || '-'}</span>
      )
    },
    {
      key: 'provRazSocial',
      label: 'RAZÓN SOCIAL',
      render: (row) => (
        <span className="text-gray-900 font-medium text-sm">{row.provRazSocial}</span>
      )
    },
    {
      key: 'provTele',
      label: 'TELÉFONO',
      render: (row) => (
        <span className="text-gray-600 text-sm">{row.provTele || '-'}</span>
      )
    },
    {
      key: 'provCiu',
      label: 'CIUDAD',
      render: (row) => (
        <span className="text-gray-600 text-sm">{row.provCiu || '-'}</span>
      )
    },
    {
      key: 'provEstado',
      label: 'ESTADO',
      render: (row) => (
        <span className={`inline-flex items-center px-2.5 py-1 rounded-full text-xs font-medium ${
          row.provEstado === 'Active' 
            ? 'bg-green-100 text-green-800'
            : 'bg-red-100 text-red-800'
        }`}>
          {row.provEstado === 'Active' ? 'Activo' : 'Inactivo'}
        </span>
      )
    },
    {
      key: 'acciones',
      label: 'ACCIONES',
      render: (row) => (
        <div className="flex items-center justify-center gap-2">
          <button 
            onClick={() => handleEdit(row)}
            className="p-2 bg-blue-500 hover:bg-blue-600 text-white rounded-lg transition-colors"
            title="Editar"
          >
            <Edit2 className="w-4 h-4" />
          </button>
          
          <RemoveButton 
            onClick={() => handleDelete(row)}
          >
            <Trash2 className="w-4 h-4" />
          </RemoveButton>
        </div>
      )
    }
  ];
  
  {/*<div className="min-h-screen bg-gray-50 p-6">*/}
  return (
    <div className="bg-gray-50 min-h-screen  "> 
      <div className="p-3 sm:p-4 max-w-7xl mx-auto">
        
        {/* Header */}
        <div className="mb-4">
          <h1 className="text-lg sm:text-xl font-bold text-gray-800 mb-1">
            Gestión Central de Proveedores
          </h1>
          <p className="text-xs sm:text-sm text-gray-600">
            Administra la información de tus proveedores
          </p>
        </div>

        {/* Barra de búsqueda y botones */}
        <div className="bg-white rounded-lg shadow-sm p-3 sm:p-4 mb-4 flex flex-col sm:flex-row items-stretch sm:items-center gap-2 sm:gap-3">
          <div className="flex-1">
            <SearchInput
              value={searchTerm}
              onChange={setSearchTerm}
              placeholder="Buscar proveedor por nombre o RUC"
            />
          </div>

          <div className="flex items-center gap-3">
            <ReloadButton 
              onClick={() => fetchProveedores(searchTerm)}
              disabled={loading}
              title="Recargar"
            >
            </ReloadButton>

            <AddButton 
              onClick={handleCreate}
              
            >
              <Plus className="w-5 h-5" />
              <span className="hidden sm:inline">Agregar Proveedor</span>
              <span className="sm:hidden">Agregar</span>
            </AddButton>
          </div>
        </div>

        {/* Mostrar error si existe */}
        {error && (
          <div className="bg-red-100 border border-red-400 text-red-700 px-3 py-2 rounded text-xs sm:text-sm mb-4">
            {error}
          </div>
        )}

        {/* Tabla */}
        <div className="bg-white rounded-lg shadow-sm p-3 sm:p-4 overflow-hidden">
          {loading ? (
            <div className="text-center py-8">
              <RefreshCw className="w-8 h-8 animate-spin mx-auto text-blue-500" />
              <p className="mt-2 text-sm text-gray-600">Cargando proveedores...</p>
            </div>
          ) : (
            <>
              <div className="overflow-x-auto text-xs sm:text-sm">
                <DataTable 
                  columns={columns} 
                  data={proveedoresFiltrados} 
                />
              </div>
              
              <div className="mt-3 sm:mt-4 pt-3 border-t border-gray-200 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-2">
                <p className="text-xs sm:text-sm text-gray-600">
                  Mostrando <span className="font-semibold text-gray-800">{proveedoresFiltrados.length}</span> de <span className="font-semibold text-gray-800">{totalCount}</span> proveedores
                </p>
                {proveedoresFiltrados.length > 0 && (
                  <p className="text-xs text-gray-500">
                    Total de registros en el sistema
                  </p>
                )}
              </div>
            </>
          )}
        </div>

      </div>

      {/* Modal de formulario */}
      <ProveedorForm
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        onSubmit={handleSubmit}
        proveedor={selectedProveedor}
        mode={modalMode}
      />
    </div>
  );
};

export default SupplierPage;