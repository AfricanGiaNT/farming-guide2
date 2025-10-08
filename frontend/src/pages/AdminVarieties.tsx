import React, { useMemo, useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/Card';
import { apiService, ExtractedVariety, VarietyExtractionParams, VarietyExtractionResult, VarietyValidationResult } from '../services/api';
import { Sprout, Loader2, Filter, ShieldCheck, FileDown, AlertCircle } from 'lucide-react';
import VarietyValidationModal from '../components/admin/VarietyValidationModal';

const cropOptions = [
  'Maize',
  'Groundnut',
  'Soybean',
  'Bean',
  'Rice',
  'Cassava',
  'Sorghum',
  'Tomato',
  'Sweet Potato',
  'Cowpea',
];

interface ExtractionSummary extends VarietyExtractionResult {}

const AdminVarieties: React.FC = () => {
  const [selectedCrops, setSelectedCrops] = useState<string[]>([]);
  const [isExtracting, setIsExtracting] = useState(false);
  const [isValidating, setIsValidating] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);
  const [modalOpen, setModalOpen] = useState(false);
  const [extractionResult, setExtractionResult] = useState<ExtractionSummary | null>(null);
  const [sessionId, setSessionId] = useState<string | null>(null);

  const totalVarietiesExtracted = extractionResult?.varieties.length ?? 0;

  const selectedCropLabels = useMemo(() => {
    if (selectedCrops.length === 0) {
      return 'All crops';
    }
    return selectedCrops.join(', ');
  }, [selectedCrops]);

  const toggleCropSelection = (crop: string) => {
    setSelectedCrops(prev => {
      if (prev.includes(crop)) {
        return prev.filter(item => item !== crop);
      }
      return [...prev, crop];
    });
  };

  const handleExtractVarieties = async () => {
    setIsExtracting(true);
    setErrorMessage(null);
    setSuccessMessage(null);

    const payload: VarietyExtractionParams = {};
    if (selectedCrops.length > 0) {
      payload.crops = selectedCrops.map(crop => crop.toLowerCase());
    }

    try {
      const response = await apiService.extractVarietiesForValidation(payload);

      if (response.status === 'success') {
        setExtractionResult(response.data);
        setSessionId(response.data.session_id);
        setSuccessMessage(response.message || 'Varieties extracted successfully.');

        if (response.data.session_id && response.data.varieties.length > 0) {
          setModalOpen(true);
        } else {
          setModalOpen(false);
        }
      } else {
        setErrorMessage(response.message || 'Failed to extract varieties.');
      }
    } catch (error) {
      console.error('Variety extraction failed', error);
      setErrorMessage('Extraction failed. Check backend logs for details.');
    } finally {
      setIsExtracting(false);
    }
  };

  const handleValidationSubmit = async (varieties: ExtractedVariety[]) => {
    if (!sessionId) {
      setErrorMessage('Session not found. Please extract varieties again.');
      return;
    }

    setIsValidating(true);
    setErrorMessage(null);

    try {
      const response = await apiService.validateSelectedVarieties({
        session_id: sessionId,
        selected_varieties: varieties,
      });

      if (response.status === 'success') {
        const data: VarietyValidationResult = response.data;
        setSuccessMessage(response.message || `Saved ${data.varieties_saved} varieties.`);
        setModalOpen(false);
        setExtractionResult(null);
      } else {
        setErrorMessage(response.message || 'Validation failed.');
      }
    } catch (error) {
      console.error('Variety validation failed', error);
      setErrorMessage('Validation failed. Please try again.');
    } finally {
      setIsValidating(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-2">
        <h1 className="flex items-center gap-2 text-3xl font-bold text-gray-900">
          <Sprout className="text-green-600" />
          Varieties Extraction Workflow
        </h1>
        <p className="max-w-3xl text-gray-600">
          Launch the varieties extraction pipeline, review detected varieties, and validate the ones that meet quality standards before saving them into the knowledge base.
        </p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-lg">
            <Filter size={20} className="text-green-600" />
            Extraction Filters
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <p className="text-sm font-medium text-gray-700">Target Crops</p>
            <p className="text-xs text-gray-500">Select specific crops or leave empty to process all available crops.</p>
          </div>
          <div className="grid grid-cols-2 gap-2 md:grid-cols-5">
            {cropOptions.map(crop => (
              <button
                key={crop}
                onClick={() => toggleCropSelection(crop)}
                className={`rounded-lg border px-3 py-2 text-sm transition ${
                  selectedCrops.includes(crop)
                    ? 'border-green-500 bg-green-50 text-green-700 shadow-sm'
                    : 'border-gray-200 text-gray-600 hover:border-green-300 hover:text-green-600'
                }`}
              >
                {crop}
              </button>
            ))}
          </div>

          <div className="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
            <p className="text-sm text-gray-600">
              <span className="font-medium text-gray-800">Selected Crops:</span> {selectedCropLabels}
            </p>
            <button
              onClick={handleExtractVarieties}
              disabled={isExtracting}
              className={`flex items-center gap-2 rounded-lg px-4 py-2 text-sm font-semibold text-white transition ${
                isExtracting ? 'bg-gray-400 cursor-not-allowed' : 'bg-green-600 hover:bg-green-700'
              }`}
            >
              {isExtracting ? <Loader2 className="animate-spin" size={18} /> : <FileDown size={18} />}
              {isExtracting ? 'Extracting…' : 'Extract Varieties'}
            </button>
          </div>
        </CardContent>
      </Card>

      {extractionResult && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-lg">
              <ShieldCheck size={20} className="text-green-600" />
              Extraction Summary
            </CardTitle>
          </CardHeader>
          <CardContent className="grid gap-4 md:grid-cols-3">
            <div className="rounded-lg border border-green-100 bg-green-50 p-4">
              <p className="text-xs font-semibold uppercase text-green-600">Session</p>
              <p className="text-sm text-gray-700">{sessionId || '—'}</p>
            </div>
            <div className="rounded-lg border border-gray-200 bg-white p-4">
              <p className="text-xs font-semibold uppercase text-gray-500">Varieties Found</p>
              <p className="text-xl font-semibold text-gray-900">{totalVarietiesExtracted}</p>
            </div>
            <div className="rounded-lg border border-gray-200 bg-white p-4">
              <p className="text-xs font-semibold uppercase text-gray-500">Documents Processed</p>
              <p className="text-xl font-semibold text-gray-900">{extractionResult.stats.documents_processed}</p>
            </div>
          </CardContent>
        </Card>
      )}

      {(errorMessage || successMessage) && (
        <div
          className={`flex items-center gap-3 rounded-lg border px-4 py-3 text-sm ${
            errorMessage
              ? 'border-red-200 bg-red-50 text-red-700'
              : 'border-green-200 bg-green-50 text-green-700'
          }`}
        >
          {errorMessage ? <AlertCircle size={18} /> : <ShieldCheck size={18} />}
          <span>{errorMessage || successMessage}</span>
        </div>
      )}

      <VarietyValidationModal
        isOpen={modalOpen}
        sessionId={sessionId}
        varieties={extractionResult?.varieties || []}
        onClose={() => setModalOpen(false)}
        onSubmit={handleValidationSubmit}
        isSubmitting={isValidating}
      />
    </div>
  );
};

export default AdminVarieties;
