'use client';

import { useState } from 'react';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faFile, faCheckCircle, faTimesCircle, faSpinner } from '@fortawesome/free-solid-svg-icons';

const requiredFiles = {
  buy: [
    { name: 'user_profile', label: 'Perfil del Usuario' },
    { name: 'bank_evidence', label: 'Datos Bancarios Usuario' },
    { name: 'titularity_proof', label: 'Prueba de Titularidad' },
    { name: 'user_payment_proof', label: 'Comprobante Bancario' },
    { name: 'user_chat', label: 'Chat del Usuario' },
    { name: 'binance_report', label: 'Informe de Binance' }
  ],
  sell: [
    { name: 'bank_evidence', label: 'Comprobante Bancario' },
    { name: 'user_payment_proof', label: 'Comprobante de Pago del Usuario' },
    { name: 'user_chat', label: 'Chat del Usuario' },
    { name: 'titularity_proof', label: 'Prueba de Titularidad' },
    { name: 'user_profile', label: 'Perfil del Usuario' },
    { name: 'binance_report', label: 'Informe de Binance' }
  ]
};

export default function HomePage() {
  const [formData, setFormData] = useState({
    order_number: '',
    transaction_type: '',
    verification_status: '',
  });
  const [fileStatus, setFileStatus] = useState({});
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleFileChange = (event) => {
    const { name, files } = event.target;
    setFileStatus(prev => ({
      ...prev,
      [name]: files[0]
    }));
  };

  const isFormValid = () => {
    const hasRequiredFields = formData.order_number && formData.transaction_type && formData.verification_status;
    if (!hasRequiredFields) return false;
    
    if (formData.transaction_type) {
      const allFilesPresent = requiredFiles[formData.transaction_type].every(file => fileStatus[file.name]);
      return allFilesPresent;
    }
    return false;
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    setIsSubmitting(true);
    
    const data = new FormData();
    data.append('order_number', formData.order_number);
    data.append('transaction_type', formData.transaction_type);
    data.append('verification_status', formData.verification_status);

    // Corrige la forma en que se añaden los archivos al formulario
    requiredFiles[formData.transaction_type].forEach(file => {
      data.append(file.name, fileStatus[file.name]);
    });

    try {
      const response = await fetch('http://localhost:8000/generate-report/', {
        method: 'POST',
        body: data,
      });

      if (!response.ok) {
        throw new Error(`Error: ${response.status} ${response.statusText}`);
      }

      const result = await response.json();
      console.log('Success:', result);
      alert('Reporte generado con éxito!');
    } catch (error) {
      console.error('Error:', error);
      alert('Ocurrió un error al generar el reporte.');
    } finally {
      setIsSubmitting(false);
    }
  };

  const renderFileInput = (name, label) => (
    <div key={name} className="flex items-center mb-2 p-2 border rounded-md shadow-sm bg-gray-50">
      <div className="flex-1">
        <label htmlFor={name} className="block text-sm font-medium text-gray-700">{label}:</label>
        <p className="mt-1 text-xs text-gray-500">
          {fileStatus[name] ? fileStatus[name].name : 'Ningún archivo seleccionado'}
        </p>
      </div>
      <label htmlFor={name} className="cursor-pointer text-sm font-medium text-indigo-600 hover:text-indigo-500">
        <FontAwesomeIcon icon={faFile} className="mr-2" />
        Seleccionar
      </label>
      <input 
        type="file" 
        id={name} 
        name={name} 
        onChange={handleFileChange}
        className="hidden"
        required
      />
    </div>
  );

  return (
    <div className="min-h-screen bg-gray-100 flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8 bg-white p-10 rounded-xl shadow-lg">
        <div>
          <h2 className="mt-6 text-center text-3xl font-extrabold text-gray-900">
            Generador de Reportes P2P
          </h2>
        </div>
        <form className="mt-8 space-y-6" onSubmit={handleSubmit}>
          <div className="rounded-md shadow-sm -space-y-px">
            <div>
              <label htmlFor="order_number" className="sr-only">Número de Orden</label>
              <input
                id="order_number"
                name="order_number"
                type="text"
                required
                className="appearance-none rounded-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-t-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 focus:z-10 sm:text-sm"
                placeholder="Número de Orden"
                value={formData.order_number}
                onChange={handleInputChange}
              />
            </div>
            <div>
              <label htmlFor="transaction_type" className="sr-only">Tipo de Transacción</label>
              <select
                id="transaction_type"
                name="transaction_type"
                required
                value={formData.transaction_type}
                onChange={handleInputChange}
                className="mt-4 appearance-none rounded-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 focus:z-10 sm:text-sm"
              >
                <option value="">Seleccione tipo de transacción</option>
                <option value="buy">Compra</option>
                <option value="sell">Venta</option>
              </select>
            </div>
            <div>
              <label htmlFor="verification_status" className="sr-only">Estado de Verificación</label>
              <select
                id="verification_status"
                name="verification_status"
                required
                value={formData.verification_status}
                onChange={handleInputChange}
                className="mt-4 appearance-none rounded-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-b-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 focus:z-10 sm:text-sm"
              >
                <option value="">Seleccione estado de verificación</option>
                <option value="approved">Aprobado</option>
                <option value="rejected">Rechazado</option>
              </select>
            </div>
          </div>

          {formData.transaction_type && (
            <div className="mt-4">
              <h3 className="text-lg font-bold mb-4">Adjuntar Documentos</h3>
              {requiredFiles[formData.transaction_type].map(file => renderFileInput(file.name, file.label))}
            </div>
          )}

          <div>
            <button
              type="submit"
              disabled={!isFormValid() || isSubmitting}
              className={`group relative w-full flex justify-center py-2 px-4 border border-transparent text-sm font-medium rounded-md text-white ${
                !isFormValid() || isSubmitting ? 'bg-gray-400 cursor-not-allowed' : 'bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500'
              }`}
            >
              {isSubmitting ? (
                <FontAwesomeIcon icon={faSpinner} spin className="mr-2" />
              ) : (
                'Generar Reporte'
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}