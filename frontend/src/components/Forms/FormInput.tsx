import React from "react";

interface FormInputProps {
  label: string;
  type?: 'text' | 'email' | 'tel' | 'number' | 'select' | 'date';
  name: string;
  value: string;
  onChange: (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => void;
  error?: string;
  required?: boolean; 
  placeholder?: string;
  disabled?: boolean;
  maxLength?: number;
  options?: { value: string; label: string }[];
  showSuccess?: boolean;
}

const FormInput: React.FC<FormInputProps> = ({
  label,
  type = 'text',
  name,
  value,
  onChange,
  error,
  required = false,
  placeholder = '',
  disabled = false,
  maxLength,
  options = [],
  showSuccess = false
}) => {
  const hasValue = value && value.trim().length > 0;
  const isValid = hasValue && !error;
  
  return (
    <div className="mb-4">
      <label htmlFor={name} className="block text-sm font-medium text-gray-700 mb-2">
        {label}
        {required && <span className="text-red-500 ml-1">*</span>}
      </label>
      
      {type === 'select' ? (
        <div className="relative">
          <select
            id={name}
            name={name}
            value={value}
            onChange={onChange}
            disabled={disabled}
            className={`w-full px-4 py-2 pr-10 border-2 rounded-lg focus:ring-2 focus:outline-none transition-colors ${
              error 
                ? 'border-red-300 bg-red-50 focus:ring-red-500 focus:border-red-500' 
                : isValid && showSuccess
                ? 'border-green-300 bg-green-50 focus:ring-green-500 focus:border-green-500'
                : 'border-gray-300 focus:ring-blue-500 focus:border-blue-500'
            } ${disabled ? 'bg-gray-100 cursor-not-allowed' : ''}`}
          >
            {options.map((option) => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
          {isValid && showSuccess && (
            <div className="absolute right-3 top-1/2 transform -translate-y-1/2">
              <svg className="w-5 h-5 text-green-500" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
              </svg>
            </div>
          )}
        </div>
      ) : (
        <div className="relative">
          <input
            id={name}
            name={name}
            type={type}
            value={value}
            onChange={onChange}
            placeholder={placeholder}
            disabled={disabled}
            maxLength={maxLength}
            className={`w-full px-4 py-2 pr-10 border-2 rounded-lg focus:ring-2 focus:outline-none transition-colors ${
              error 
                ? 'border-red-300 bg-red-50 focus:ring-red-500 focus:border-red-500' 
                : isValid && showSuccess
                ? 'border-green-300 bg-green-50 focus:ring-green-500 focus:border-green-500'
                : 'border-gray-300 focus:ring-blue-500 focus:border-blue-500'
            } ${disabled ? 'bg-gray-100 cursor-not-allowed' : ''}`}
          />
          {isValid && showSuccess && (
            <div className="absolute right-3 top-1/2 transform -translate-y-1/2">
              <svg className="w-5 h-5 text-green-500" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
              </svg>
            </div>
          )}
        </div>
      )}

      {error && (
        <div className="mt-2 flex items-start gap-2 p-2 bg-red-50 border border-red-200 rounded-md">
          <svg className="w-4 h-4 text-red-500 mt-0.5 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
          </svg>
          <p className="text-sm text-red-700 font-medium">{error}</p>
        </div>
      )}
    </div>
  );
};

export default FormInput;