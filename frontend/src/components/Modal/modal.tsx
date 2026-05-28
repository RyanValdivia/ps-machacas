import React, { useEffect } from 'react';
import { X } from 'lucide-react';

interface ModalProps {
  isOpen: boolean;
  onClose: () => void;
  title: string;
  children: React.ReactNode;
  size?: 'sm' | 'md' | 'lg' | 'xl';
}

const Modal: React.FC<ModalProps> = ({ 
  isOpen, 
  onClose, 
  title, 
  children,
  size = 'md' 
}) => {
  // Cerrar con tecla Escape
  useEffect(() => {
    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape' && isOpen) {
        onClose();
      }
    };

    if (isOpen) {
      document.addEventListener('keydown', handleEscape);
      // Prevenir scroll del body cuando el modal está abierto
      document.body.style.overflow = 'hidden';
    }

    return () => {
      document.removeEventListener('keydown', handleEscape);
      document.body.style.overflow = 'unset';
    };
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  // Clases de tamaño con responsive
  const sizeClasses = {
    sm: 'max-w-md w-full mx-4',
    md: 'max-w-2xl w-full mx-4',
    lg: 'max-w-4xl w-full mx-4',
    xl: 'max-w-3xl w-full mx-4'
  };

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto">
      {/* Overlay sutil con animación */}
      <div 
        className={`fixed inset-0 bg-black/20 backdrop-blur-sm transition-opacity duration-300 ${
          isOpen ? 'opacity-100' : 'opacity-0'
        }`}
        onClick={onClose}
      />

      {/* Contenedor del modal con animación */}
      <div className="flex min-h-full items-center justify-center p-2 sm:p-4">
        <div 
          className={`relative bg-white rounded-lg shadow-xl ${sizeClasses[size]} max-h-[95vh] flex flex-col transform transition-all duration-300 ${
            isOpen ? 'opacity-100 scale-100 translate-y-0' : 'opacity-0 scale-95 translate-y-4'
          }`}
          onClick={(e) => e.stopPropagation()}
        >
          {/* Header del modal */}
          <div className="flex items-center justify-between p-3 sm:p-4 lg:p-6 border-b border-gray-200 flex-shrink-0">
            <h3 className="text-base sm:text-lg lg:text-xl font-semibold text-gray-900">
              {title}
            </h3>
            <button
              onClick={onClose}
              className="text-gray-400 hover:text-gray-600 transition-colors p-1 rounded-lg hover:bg-gray-100"
              aria-label="Cerrar modal"
            >
              <X className="w-5 h-5 sm:w-6 sm:h-6" />
            </button>
          </div>

          {/* Contenido del modal con scroll */}
          <div className="p-3 sm:p-4 lg:p-6 overflow-y-auto flex-1">
            {children}
          </div>
        </div>

      </div>
    </div>
  );
};

export default Modal;
