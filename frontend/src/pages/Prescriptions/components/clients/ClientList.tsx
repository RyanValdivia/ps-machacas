import DataTable from "../../../../components/Table/DataTable";
import type { Column } from "../../../../components/Table/DataTable";
import type { Client } from "../../../../types/client";
import { Eye } from "lucide-react";

type Props = {
  clients: Client[];
  loading: boolean;
  onSelect: (client: Client) => void;
};

const ClientList = ({ clients, loading, onSelect }: Props) => {
  const formatDate = (dateString: string | null | undefined) => {
    if (!dateString) return 'N/A';

    // Si la fecha viene en formato YYYY-MM-DD, parsearla directamente sin zona horaria
    if (typeof dateString === 'string' && dateString.match(/^\d{4}-\d{2}-\d{2}/)) {
      const [year, month, day] = dateString.split('-');
      return `${day}/${month}/${year}`;
    }

    // Si viene en otro formato, intentar parsearla pero usando solo la fecha local
    const date = new Date(dateString);
    if (isNaN(date.getTime())) return 'N/A';

    // Usar métodos locales para evitar problemas de zona horaria
    const day = String(date.getDate()).padStart(2, '0');
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const year = date.getFullYear();
    return `${day}/${month}/${year}`;
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

  const getClientAge = (client: Client): string => {
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
    
    return 'N/A';
  };

  const columns: Column<Client>[] = [
    { key: "cliNumDoc", label: "DNI" },
    { key: "cliNomCompleto", label: "NOMBRE" },
    { key: "cliTelef", label: "TELEFONO" },
    {
      key: "edad",
      label: "EDAD",
      render: (row) => (
        <span>{getClientAge(row)}</span>
      )
    },
    {
      key: "cliFechaNac",
      label: "FECHA NACIMIENTO",
      render: (row) => <span>{formatDate(row.cliFechaNac)}</span>
    },
    {
      key: "actions",
      label: "ACCIONES",
      render: (row) => (
        <div className="flex items-center justify-center gap-2">
          <button
            onClick={() => onSelect(row)}
            className="flex items-center gap-1 px-3 py-1.5 bg-indigo-500 hover:bg-indigo-600 text-white rounded-lg transition-all hover:scale-105 shadow-sm text-sm font-medium"
            title="Ver detalle del cliente"
          >
            <Eye className="w-4 h-4" />

          </button>
        </div>
      ),
    }
  ];

  // Control de carga aquí
  if (loading) {
    return (
      <div className="py-4 text-center text-gray-500">
        Cargando clientes...
      </div>
    );
  }

  return <DataTable columns={columns} data={clients} />;
};

export default ClientList;
