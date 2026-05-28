import { Package, AlertCircle } from 'lucide-react';
import type { User } from '../types/user';

interface NoCashAssignedProps {
  user: User;
}

export default function NoCashAssigned({ user }: NoCashAssignedProps) {
  return (
    <div className="min-h-screen flex items-center justify-center p-4">
      <div className="max-w-md w-full bg-white rounded-2xl shadow-xl p-12 text-center">
        <div className="mb-6">
          <div className="relative inline-block">
            <Package className="w-20 h-20 text-gray-300 mx-auto" strokeWidth={1.5} />
            <AlertCircle className="w-8 h-8 text-orange-500 absolute -bottom-1 -right-1 bg-white rounded-full" />
          </div>
        </div>

        <h2 className="text-2xl font-bold text-gray-800 mb-3">
          Sin Caja Asignada
        </h2>
        
        <p className="text-gray-600 mb-2">
          Hola <span className="font-semibold text-gray-800">{user.usuNombreCom}</span>
        </p>
        
        <p className="text-gray-600 mb-6">
          No tienes una caja registradora asignada. Necesitas que un administrador te asigne una caja.
        </p>

        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
          <p className="text-sm text-blue-800">
            <strong>¿Qué hacer?</strong>
            <br />
            Contacta al administrador del sistema para que te asigne una caja registradora.
          </p>
        </div>

        <div className="flex flex-col gap-3">
          <a
            href="/dashboard"
            className="w-full px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium"
          >
            Ir al Dashboard
          </a>
          
          <button
            onClick={() => window.location.reload()}
            className="w-full px-6 py-3 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors font-medium"
          >
            Reintentar
          </button>
        </div>

      </div>
    </div>
  );
}
