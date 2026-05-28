import { ChevronLeft, ChevronRight } from 'lucide-react';

interface Props {
  page: number;
  next: string | null;
  previous: string | null;
  onPageChange: (page: number) => void;
}

const Pagination = ({ page, next, previous, onPageChange }: Props) => {
  return (
    <div className="flex justify-center items-center gap-2 mt-6">
      <button
        disabled={!previous}
        onClick={() => onPageChange(page - 1)}
        className="flex items-center gap-1 px-4 py-2 bg-white border border-gray-300 rounded-lg
                   disabled:opacity-50 disabled:cursor-not-allowed
                   hover:bg-gray-50 transition-colors
                   text-sm font-medium text-gray-700"
      >
        <ChevronLeft className="w-4 h-4" />
        Anterior
      </button>

      <div className="flex items-center gap-2 px-4 py-2 bg-[#3BAEDF] text-white rounded-lg font-semibold min-w-[100px] justify-center">
        Página {page}
      </div>

      <button
        disabled={!next}
        onClick={() => onPageChange(page + 1)}
        className="flex items-center gap-1 px-4 py-2 bg-white border border-gray-300 rounded-lg
                   disabled:opacity-50 disabled:cursor-not-allowed
                   hover:bg-gray-50 transition-colors
                   text-sm font-medium text-gray-700"
      >
        Siguiente
        <ChevronRight className="w-4 h-4" />
      </button>
    </div>
  );
};

export default Pagination;
