"use client";

import React from "react";

export type Column<T> = {
  key: keyof T | string;
  label: string;
  render?: (row: T) => React.ReactNode;
};

type Props<T> = {
  columns: Column<T>[];
  data: T[];
  onRowClick?: (row: T) => void;
  getRowClassName?: (row: T) => string;
};

export default function DataTable<T>({ columns, data, onRowClick, getRowClassName }: Props<T>) {
  return (
    <div className="border border-gray-200 rounded-lg shadow-sm">
      <table className="w-full text-xs text-center">
        <thead className="bg-gray-100 text-gray-700">
          <tr>
            {columns.map((col) => (
              <th key={col.key.toString()} className="px-3 2xl:px-4 py-2 2xl:py-3 font-medium bg-gray-100 text-xs 2xl:text-sm whitespace-nowrap">
                {col.label}
              </th>
            ))}
          </tr>
        </thead>
        <tbody className="divide-y divide-gray-200 bg-white">
          {data.map((row, idx) => {
            const customClassName = getRowClassName ? getRowClassName(row) : '';
            return (
              <tr
                key={idx}
                className={`transition-colors ${customClassName} ${
                  onRowClick ? "cursor-pointer" : ""
                }`}
                onClick={() => onRowClick?.(row)}
              >
                {columns.map((col) => (
                  <td key={col.key.toString()} className="px-3 2xl:px-4 py-2 2xl:py-3 text-xs 2xl:text-sm">
                    {col.render ? col.render(row) : (row[col.key as keyof T] as React.ReactNode)}
                  </td>
                ))}
              </tr>
            );
          })}
        </tbody>
      </table>

      {data.length === 0 && (
        <div className="text-center text-gray-500 py-6 2xl:py-8 bg-white text-sm 2xl:text-base">No hay datos disponibles</div>
      )}
    </div>
  );
}
