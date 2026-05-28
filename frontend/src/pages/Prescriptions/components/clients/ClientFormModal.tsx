import React, { useState, useEffect } from "react";
import Modal from "../../../../components/Modal/modal";
import FormInput from "../../../../components/Forms/FormInput";
import type { Client } from "../../../../types/client";

type Props = {
  open: boolean;
  onClose: () => void;
  onSave: (client: Client) => void;
  client?: Client | null; // Para editar
};

type TipoDoc = "DNI" | "CE";

const ClientFormModal = ({ open, onClose, onSave, client }: Props) => {
  const [form, setForm] = useState<Partial<Client> & { cliTipoDoc: TipoDoc }>({
    cliTipoDoc: "DNI",
    cliNomCompleto: "",
    cliNumDoc: "",
    cliTelef: "",
    cliFechaNac: "",
  });

  // Rellenar el formulario cuando cambie el cliente o se abra el modal
  useEffect(() => {
    if (open) {
      if (client) {
        // Formatear la fecha para el input type="date" (YYYY-MM-DD)
        let fechaFormateada = "";
        if (client.cliFechaNac) {
          // Si la fecha viene en formato YYYY-MM-DD, usarla directamente
          if (typeof client.cliFechaNac === 'string' && client.cliFechaNac.match(/^\d{4}-\d{2}-\d{2}/)) {
            fechaFormateada = client.cliFechaNac;
          } else {
            // Si viene en otro formato, parsearla pero usando solo la fecha local
            // Crear la fecha en zona horaria local para evitar problemas
            const fechaStr = client.cliFechaNac.toString();
            const fecha = new Date(fechaStr + 'T00:00:00'); // Agregar hora para evitar conversión UTC

            if (!isNaN(fecha.getTime())) {
              // Tomamos año, mes y día directamente en local
              const yyyy = fecha.getFullYear();
              const mm = String(fecha.getMonth() + 1).padStart(2, "0");
              const dd = String(fecha.getDate()).padStart(2, "0");
              fechaFormateada = `${yyyy}-${mm}-${dd}`;
            }
          }
        }


        setForm({
          cliTipoDoc: (client.cliTipoDoc as TipoDoc) || "DNI",
          cliNomCompleto: client.cliNomCompleto || "",
          cliNumDoc: client.cliNumDoc || "",
          cliTelef: client.cliTelef || "",
          cliFechaNac: fechaFormateada,
        });
      } else {
        // Resetear formulario para nuevo cliente
        setForm({
          cliTipoDoc: "DNI",
          cliNomCompleto: "",
          cliNumDoc: "",
          cliTelef: "",
          cliFechaNac: "",
        });
      }
    }
  }, [client, open]);

  const handleChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>
  ) => {
    const { name, value } = e.target;

    // Para cliTipoDoc aseguramos que solo sea "DNI" | "CE"
    if (name === "cliTipoDoc" && (value === "DNI" || value === "CE")) {
      setForm({ ...form, cliTipoDoc: value });
    } else {
      setForm({ ...form, [name]: value });
    }
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

  const handleSubmit = () => {
    // Calcular edad automáticamente a partir de la fecha de nacimiento
    const edad = calculateAge(form.cliFechaNac);
    
    const clientData = {
      ...form,
      cliFechaNac: form.cliFechaNac || null,
      edad: edad,
    };
    onSave(clientData as Client);
    onClose();
  };

  return (
    <Modal
      isOpen={open}
      onClose={onClose}
      title={client ? "Editar Cliente" : "Agregar Cliente"}
      size="lg"
    >
      {/* Aviso de validación */}
      <div className="mb-4 p-3 rounded-md bg-yellow-50 border border-yellow-200 flex items-center text-sm text-yellow-700">
        <svg
          xmlns="http://www.w3.org/2000/svg"
          className="h-5 w-5 mr-2 text-yellow-500"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M12 9v2m0 4h.01M12 5a7 7 0 100 14a7 7 0 000-14z"
          />
        </svg>
        <span>
          Recuerda: no se podrá registrar un cliente nuevo si el número de DNI ya existe en el sistema.
        </span>
      </div >
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Tipo DOCUMENTO */}
          <FormInput
            label="Tipo de documento"
            name="cliTipoDoc"
            type="select"
            value={form.cliTipoDoc}
            onChange={handleChange}
            required
            options={[
              { value: "DNI", label: "DNI" },
              { value: "CE", label: "Carnet de extranjería" },
            ]}
            placeholder="DNI"
            maxLength={13}
          />

          {/* Nro DOCUMENTO */}
          <FormInput
            label="Numero de documento"
            name="cliNumDoc"
            type="text"
            value={form.cliNumDoc || ""}
            onChange={handleChange}
            required
            placeholder=""
            maxLength={13}
          />
        
          {/* Nombre Completo */}
          <FormInput
            label="Nombre completo"
            name="cliNomCompleto"
            type="text"
            value={form.cliNomCompleto || ""}
            onChange={handleChange}
            required
            placeholder=""
            maxLength={40}
          />
          {/* Nombre Completo */}
          <FormInput
            label="Numero Celular"
            name="cliTelef"
            type="text"
            value={form.cliTelef || ""}
            onChange={handleChange}
            required
            placeholder=""
            maxLength={9}
          />
        {/* Fecha de Nacimiento */}
          <div>
            <FormInput
              label="Fecha de Nacimiento"
              name="cliFechaNac"
              type="date"
              value={form.cliFechaNac || ""}
              onChange={handleChange}
              required
              placeholder=""
              maxLength={30}
            />
            {form.cliFechaNac && calculateAge(form.cliFechaNac) !== null && (
              <p className="text-sm text-gray-600 mt-1">
                Edad: <span className="font-semibold">{calculateAge(form.cliFechaNac)} años</span>
              </p>
            )}
          </div>
      </div>

      {/* Botones de acción */}
      <div className="flex justify-end gap-3 mt-6 pt-6 border-t border-gray-200">
        <button
          type="button"
          onClick={onClose}
          className="px-6 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 transition-colors"
        >
            Cancelar
        </button>
        <button
          type="submit"
          className="px-6 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors disabled:bg-blue-300 disabled:cursor-not-allowed"
          onClick={handleSubmit}
        >
          Guardar
        </button>
      </div>
    </Modal>
  );
};

export default ClientFormModal;
