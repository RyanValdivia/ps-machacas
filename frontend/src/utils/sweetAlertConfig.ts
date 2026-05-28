import Swal from 'sweetalert2';

// Configuración base de SweetAlert2
const Toast = Swal.mixin({
  toast: true,
  position: 'top-end',
  showConfirmButton: false,
  timer: 3000,
  timerProgressBar: true,
  didOpen: (toast) => {
    toast.addEventListener('mouseenter', Swal.stopTimer);
    toast.addEventListener('mouseleave', Swal.resumeTimer);
  }
});

// Notificaciones de éxito
export const showSuccessToast = (message: string) => {
  return Toast.fire({
    icon: 'success',
    title: message
  });
};

// Notificaciones de error
export const showErrorToast = (message: string) => {
  return Toast.fire({
    icon: 'error',
    title: message
  });
};

// Notificaciones de advertencia
export const showWarningToast = (message: string) => {
  return Toast.fire({
    icon: 'warning',
    title: message
  });
};

// Notificaciones de información
export const showInfoToast = (message: string) => {
  return Toast.fire({
    icon: 'info',
    title: message
  });
};

// Alerta de éxito centrada
export const showSuccessAlert = (title: string, text?: string) => {
  return Swal.fire({
    icon: 'success',
    title: title,
    text: text,
    confirmButtonColor: '#3085d6',
    confirmButtonText: 'Aceptar'
  });
};

// Alerta de error centrada
export const showErrorAlert = (title: string, text?: string) => {
  return Swal.fire({
    icon: 'error',
    title: title,
    text: text,
    confirmButtonColor: '#d33',
    confirmButtonText: 'Aceptar'
  });
};

// Confirmación de eliminación
export const showDeleteConfirmation = (itemName: string) => {
  return Swal.fire({
    title: '¿Estás seguro?',
    html: `Se eliminará el producto:<br><strong>"${itemName}"</strong>`,
    icon: 'warning',
    showCancelButton: true,
    confirmButtonColor: '#d33',
    cancelButtonColor: '#3085d6',
    confirmButtonText: 'Sí, eliminar',
    cancelButtonText: 'Cancelar',
    reverseButtons: true
  });
};

// Confirmación genérica
export const showConfirmation = (title: string, text: string, confirmText = 'Confirmar', cancelText = 'Cancelar') => {
  return Swal.fire({
    title: title,
    text: text,
    icon: 'question',
    showCancelButton: true,
    confirmButtonColor: '#3085d6',
    cancelButtonColor: '#6c757d',
    confirmButtonText: confirmText,
    cancelButtonText: cancelText,
    reverseButtons: true
  });
};

// Loading/Cargando
export const showLoading = (title: string = 'Cargando...') => {
  return Swal.fire({
    title: title,
    allowOutsideClick: false,
    allowEscapeKey: false,
    didOpen: () => {
      Swal.showLoading();
    }
  });
};

// Cerrar loading
export const closeLoading = () => {
  Swal.close();
};
