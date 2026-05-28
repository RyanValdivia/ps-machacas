import { Users } from 'lucide-react';

interface Client {
  cliCod: number;
  cliNomCompleto: string;
  cliNumDoc: string;
  total_compras?: number;
  total_monto?: number;
}

interface ClientsTableProps {
  clients: Client[];
}

const ClientsTable = ({ clients }: ClientsTableProps) => {
  const isEmpty = !clients || clients.length === 0;

  return (
    <div className="bg-white rounded-xl shadow-lg p-6">
      <div className="flex items-center space-x-2 mb-4">
        <Users className="w-5 h-5 text-blue-500" />
        <h3 className="text-lg font-semibold text-gray-900">Clientes Frecuentes</h3>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full">
          <thead>
            <tr className="border-b-2 border-gray-200">
              <th className="text-left py-3 px-4 text-sm font-semibold text-gray-700">Nombre</th>
              <th className="text-left py-3 px-4 text-sm font-semibold text-gray-700">Documento</th>
              <th className="text-center py-3 px-4 text-sm font-semibold text-gray-700">N° Compras</th>
              <th className="text-right py-3 px-4 text-sm font-semibold text-gray-700">Total Gastado</th>
            </tr>
          </thead>
          <tbody>
            {isEmpty ? (
              <tr>
                <td colSpan={4} className="py-12 text-center">
                  <div className="flex flex-col items-center justify-center text-gray-400">
                    <Users className="w-16 h-16 mb-3 opacity-30" />
                    <p className="text-lg font-medium">No hay clientes registrados</p>
                    <p className="text-sm mt-1">Los clientes aparecerán aquí cuando realicen compras</p>
                  </div>
                </td>
              </tr>
            ) : (
              clients.slice(0, 10).map((client, idx) => (
                <tr key={client.cliCod} className={`border-b border-gray-100 hover:bg-blue-50 transition-colors ${
                  idx % 2 === 0 ? 'bg-white' : 'bg-gray-50'
                }`}>
                  <td className="py-3 px-4 text-sm font-medium text-gray-900">{client.cliNomCompleto}</td>
                  <td className="py-3 px-4 text-sm text-gray-600">{client.cliNumDoc}</td>
                  <td className="py-3 px-4 text-center">
                    <span className="inline-flex items-center px-2.5 py-1 rounded-full bg-blue-100 text-blue-700 text-sm font-semibold">
                      {client.total_compras || 0}
                    </span>
                  </td>
                  <td className="py-3 px-4 text-right text-sm font-semibold text-blue-600">
                    S/ {(client.total_monto || 0).toFixed(2)}
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default ClientsTable;
