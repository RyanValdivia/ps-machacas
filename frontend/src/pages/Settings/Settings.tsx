import SettingsTabs from "./Components/Tabs/SettingsTabs";
import { Outlet } from "react-router-dom";



export default function Settings() {

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="mb-9">
        <h1 className="text-3xl font-bold text-gray-800 mb-2">
          Configuración y Administración de acceso
        </h1>
        <p className="text-gray-600 pl-2">
          Administra, redefine y controla el acceso e información de la empresa
        </p>
      </div>
      <SettingsTabs />
      <Outlet />
    </div>
  );
}