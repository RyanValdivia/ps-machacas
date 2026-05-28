import { useState } from "react";
import { Filter, X, ChevronDown, ChevronUp, Plus } from "lucide-react";

export type ClientFilters = {
  search: string;
  cliTipoDoc: string;
  edadMin: string;
  edadMax: string;
};

type Props = {
  filters: ClientFilters;
  onChange: (filters: ClientFilters) => void;
  onNew: () => void;
};

const ClientFilters = ({ filters, onChange, onNew }: Props) => {
  const [showAdvanced, setShowAdvanced] = useState(false);

  const handleChange = (field: keyof ClientFilters, value: string) => {
    onChange({ ...filters, [field]: value });
  };

  const hasFilters =
    filters.cliTipoDoc || (filters.edadMin && filters.edadMin !== "") || (filters.edadMax && filters.edadMax !== "");

  const clearFilters = () => {
    onChange({
      search: filters.search,
      cliTipoDoc: "",
      edadMin: "",
      edadMax: "",
    });
  };

  return (
    <div className="bg-white rounded-lg shadow mb-4">

      <div className="p-4 flex gap-3 flex-col lg:flex-row">
      <input
        type="text"
        placeholder="Buscar por nombre Completo o DNI"
        value={filters.search}
        onChange={(e) => handleChange("search", e.target.value)}
        className="flex-1 rounded-lg px-3 py-2 border border-gray-300"
      />


        <button
          onClick={() => setShowAdvanced(!showAdvanced)}
          className={`flex items-center gap-2 px-4 py-2 rounded ${
            showAdvanced || hasFilters
              ? "bg-blue-600 text-white"
              : "bg-gray-100"
          }`}
        >
          <Filter size={16} />
          Filtros
          {showAdvanced ? <ChevronUp /> : <ChevronDown />}
        </button>

      </div>

      {showAdvanced && (
        <div className="border-t bg-gray-50 p-4">
          <div className="flex justify-between mb-3">
            <span className="text-sm font-semibold">Filtros avanzados</span>
            {hasFilters && (
              <button
                onClick={clearFilters}
                className="flex items-center gap-1 text-red-600 text-sm"
              >
                <X size={14} />
                Limpiar
              </button>
            )}
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {/* Tipo Documento */}
            <select
              value={filters.cliTipoDoc}
              onChange={(e) => handleChange("cliTipoDoc", e.target.value)}
              className="border rounded px-3 py-2"
            >
              <option value="">Tipo documento</option>
              <option value="DNI">DNI</option>
              <option value="CE">Carnet Extranjería</option>
            </select>

            {/* Edad mínima */}
            <input
              type="number"
              placeholder="Edad mínima"
              value={filters.edadMin}
              onChange={(e) => handleChange("edadMin", e.target.value)}
              className="border rounded px-3 py-2"
            />

            {/* Edad máxima */}
            <input
              type="number"
              placeholder="Edad máxima"
              value={filters.edadMax}
              onChange={(e) => handleChange("edadMax", e.target.value)}
              className="border rounded px-3 py-2"
            />
          </div>
        </div>
      )}
    </div>
  );
};

export default ClientFilters;
