import { useEffect, useState } from "react";
import { Plus } from "lucide-react";
import type { Client } from "../../types/client";

import ClientFilters from "./components/clients/ClientFilters";
import ClientList from "./components/clients/ClientList";
import ClientFormModal from "./components/clients/ClientFormModal";
import ClientDetailPanel from "./components/clients/ClientDetailPanel";
import Pagination from "../../components/Pagination/Pagination";
import { getClients, createClient, updateClient, deleteClient } from "../../services/clientService";
import { showSuccessToast, showErrorToast } from "../../utils/sweetAlertConfig";

const Prescriptions = () => {
  const [clients, setClients] = useState<Client[]>([]);
  const [loading, setLoading] = useState(false);

  const [page, setPage] = useState(1);
  const [next, setNext] = useState<string | null>(null);
  const [previous, setPrevious] = useState<string | null>(null);
  const [detailOpen, setDetailOpen] = useState(false); 
  const [modalOpen, setModalOpen] = useState(false);
  const [selectedClient, setSelectedClient] = useState<Client | null>(null);

  const [filters, setFilters] = useState({
    search: "",
    cliTipoDoc: "",
    edadMin: "",
    edadMax: "",
  });

  const loadClients = async (pageNumber = page) => {
    try {
      setLoading(true);

      // Preparar filtros para el backend
      const filtersForBackend = {
        cliTipoDoc: filters.cliTipoDoc || undefined,
        edad_min: filters.edadMin ? parseInt(filters.edadMin) : undefined,
        edad_max: filters.edadMax ? parseInt(filters.edadMax) : undefined,
      };

      const data = await getClients(filters.search, pageNumber, filtersForBackend);

      setClients(data.results);
      setNext(data.next);
      setPrevious(data.previous);
    } catch (error) {
      console.error("Error cargando clientes", error);
      showErrorToast("Error al cargar clientes");
    } finally {
      setLoading(false);
    }
  };

  // Recargar cuando cambien la página o filtros avanzados
  useEffect(() => {
    loadClients();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [page, filters.cliTipoDoc, filters.edadMin, filters.edadMax]);

  // Debounce para la búsqueda (esperar 500ms después de que el usuario deje de escribir)
  useEffect(() => {
    const timeoutId = setTimeout(() => {
      if (page === 1) {
        loadClients(1);
      } else {
        setPage(1);
      }
    }, 500);

    return () => clearTimeout(timeoutId);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [filters.search]);

  const handleSaveClient = async (clientData: Omit<Client, "cliCod">) => {
    try {
      if (selectedClient) {
        await updateClient(selectedClient.cliCod!, clientData);
        showSuccessToast("Cliente actualizado exitosamente");
      } else {
        await createClient(clientData);
        showSuccessToast("Cliente creado exitosamente");
      }
      setModalOpen(false);
      setSelectedClient(null);
      loadClients();
    } catch (error: any) {
      console.error("Error guardando cliente:", error.response?.data);
      const errorMsg = error.response?.data?.cliNumDoc?.[0] || "Error al guardar cliente";
      showErrorToast(errorMsg);
    }
  };


  const handleOpenClientDetail = (client: Client) => {
    setSelectedClient(client);
    setDetailOpen(true);
  };

  const handleEditFromDetail = (client: Client) => {
    setSelectedClient(client);
    setDetailOpen(false);
    setModalOpen(true);
  };



  return (
    <div className="pt-15 px-6">

      {/* ===== HEADER ===== */}
      <div className="mb-6 flex justify-between items-start">
        <div>
          <h2 className="text-3xl font-bold text-gray-800 mb-2">
            Prescripciones
          </h2>
          <p className="text-gray-600">
            Gestión de clientes y recetas oftalmológicas
          </p>
        </div>

        <button
          onClick={() => {
            setSelectedClient(null);
            setModalOpen(true);
          }}
          className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white
                     rounded-lg hover:bg-blue-700 transition-colors shadow-sm"
        >
          <Plus className="w-5 h-5" />
          Nuevo Cliente
        </button>
      </div>

      {/* ===== BUSCADOR ===== */}
      <ClientFilters
        filters={filters}
        onChange={setFilters}
        onNew={() => {
          setSelectedClient(null);
          setModalOpen(true);
        }}
      />

      {/* ===== LISTA ===== */}
      <ClientList
        clients={clients}
        loading={loading}
        onSelect={handleOpenClientDetail}
      />
      <div className="mt-8">
        {/* ===== PAGINACIÓN ===== */}
        <Pagination
          page={page}
          next={next}
          previous={previous}
          onPageChange={setPage}
        />
      </div>
      {/* ===== MODAL ===== */}
      <ClientFormModal
        open={modalOpen}
        onClose={() => {
          setModalOpen(false);
          setSelectedClient(null);
        }}
        onSave={handleSaveClient}
        client={selectedClient}
      />

      {/*PANEL DETALLE */}
      <ClientDetailPanel
        client={selectedClient}
        open={detailOpen}
        onClose={() => {
          setDetailOpen(false);
        }}
        onEdit={handleEditFromDetail}
        onRefresh={loadClients}
      />
    </div>
  );
};

export default Prescriptions;
