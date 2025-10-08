import React, { useEffect, useMemo, useState } from 'react';
import { ExtractedVariety } from '../../services/api';
import {
  X,
  CheckSquare,
  Square,
  ShieldCheck,
  AlertCircle,
  ArrowRightCircle,
} from 'lucide-react';

interface VarietyValidationModalProps {
  isOpen: boolean;
  sessionId: string | null;
  varieties: ExtractedVariety[];
  onClose: () => void;
  onSubmit: (selectedVarieties: ExtractedVariety[]) => Promise<void> | void;
  isSubmitting?: boolean;
}

type SelectableVariety = ExtractedVariety & { _selectionKey: string };

const VarietyValidationModal: React.FC<VarietyValidationModalProps> = ({
  isOpen,
  sessionId,
  varieties,
  onClose,
  onSubmit,
  isSubmitting = false,
}) => {
  const [selectedKeys, setSelectedKeys] = useState<Set<string>>(new Set());
  const [searchTerm, setSearchTerm] = useState('');

  useEffect(() => {
    if (!isOpen) {
      setSelectedKeys(new Set());
      setSearchTerm('');
    }
  }, [isOpen]);

  useEffect(() => {
    // Reset selection when a new session is loaded
    setSelectedKeys(new Set());
  }, [sessionId]);

  const toggleSelection = (key: string) => {
    setSelectedKeys(prev => {
      const newSet = new Set(prev);
      if (newSet.has(key)) {
        newSet.delete(key);
      } else {
        newSet.add(key);
      }
      return newSet;
    });
  };

  const selectableVarieties: SelectableVariety[] = useMemo(
    () =>
      varieties.map((variety, index) => ({
        ...variety,
        _selectionKey: `${variety.variety_name || 'variety'}-${variety.crop_name}-${index}`,
      })),
    [varieties]
  );

  const filteredVarieties: SelectableVariety[] = useMemo(() => {
    return selectableVarieties
      .filter(variety => {
        if (!searchTerm) return true;
        const haystack = [
          variety.variety_name,
          variety.crop_name,
          variety.variety_type,
          variety.source_document,
        ]
          .filter(Boolean)
          .join(' ')
          .toLowerCase();
        return haystack.includes(searchTerm.toLowerCase());
      });
  }, [selectableVarieties, searchTerm]);

  const handleSelectAll = () => {
    setSelectedKeys(new Set(filteredVarieties.map(v => v._selectionKey)));
  };

  const handleDeselectAll = () => {
    setSelectedKeys(new Set());
  };

  const selectedVarieties = selectableVarieties.filter(variety => selectedKeys.has(variety._selectionKey));
  const totalSelected = selectedVarieties.length;

  const handleSubmit = async () => {
    if (selectedVarieties.length === 0) {
      return;
    }

    await onSubmit(selectedVarieties.map(({ _selectionKey, ...rest }) => rest));
  };

  if (!isOpen) {
    return null;
  }

  const renderConfidenceBadge = (score: number | undefined) => {
    if (typeof score !== 'number') {
      return <span className="text-xs text-gray-500">No score</span>;
    }

    const confidenceColor = score >= 80 ? 'bg-green-100 text-green-700' : score >= 60 ? 'bg-amber-100 text-amber-700' : 'bg-red-100 text-red-700';

    return (
      <span className={`px-2 py-1 rounded-full text-xs font-medium ${confidenceColor}`}>
        Confidence {score}%
      </span>
    );
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50 p-4">
      <div className="w-full max-w-5xl rounded-2xl bg-white shadow-xl">
        <div className="flex items-center justify-between border-b border-gray-200 px-6 py-4">
          <div>
            <h2 className="text-xl font-semibold text-gray-900">Validate Extracted Varieties</h2>
            <p className="text-sm text-gray-600">
              Review and select the varieties you want to add to the database. Session ID: {sessionId || '—'}
            </p>
          </div>
          <button
            onClick={onClose}
            className="rounded-full p-2 text-gray-500 transition hover:bg-gray-100"
            aria-label="Close validation modal"
          >
            <X size={20} />
          </button>
        </div>

        <div className="border-b border-gray-200 bg-gray-50 px-6 py-3">
          <div className="flex flex-wrap items-center gap-4">
            <div className="flex items-center gap-2">
              <ShieldCheck className="text-green-600" size={18} />
              <span className="text-sm text-gray-700">
                Stage 2 of 3 · Validate extracted varieties before saving
              </span>
            </div>
            <div className="ml-auto flex items-center gap-3 text-sm text-gray-600">
              <span>{totalSelected} selected</span>
              <span className="text-gray-400">|</span>
              <span>{filteredVarieties.length} varieties detected</span>
            </div>
          </div>
        </div>

        <div className="px-6 py-4">
          <div className="mb-4 flex flex-col gap-3 md:flex-row md:items-center">
            <div className="flex flex-1 items-center gap-2">
              <input
                type="text"
                value={searchTerm}
                onChange={event => setSearchTerm(event.target.value)}
                placeholder="Search varieties, crops, or sources"
                className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-green-500 focus:outline-none focus:ring-2 focus:ring-green-200"
              />
            </div>
            <div className="flex gap-2">
              <button
                onClick={handleSelectAll}
                className="flex items-center gap-2 rounded-lg border border-green-200 px-3 py-2 text-sm text-green-700 transition hover:bg-green-50"
              >
                <CheckSquare size={18} />
                Select All
              </button>
              <button
                onClick={handleDeselectAll}
                className="flex items-center gap-2 rounded-lg border border-gray-200 px-3 py-2 text-sm text-gray-600 transition hover:bg-gray-50"
              >
                <Square size={18} />
                Deselect All
              </button>
            </div>
          </div>

          <div className="max-h-[480px] space-y-3 overflow-y-auto pr-1">
            {filteredVarieties.length === 0 && (
              <div className="flex items-center gap-3 rounded-lg border border-gray-200 bg-white px-4 py-6 text-gray-600">
                <AlertCircle className="text-amber-500" size={22} />
                <span>No varieties match your search filter.</span>
              </div>
            )}

            {filteredVarieties.map(variety => {
              const selected = selectedKeys.has(variety._selectionKey);
              const confidence = variety.confidence_score ?? 0;
              const previewContext = variety.context ? `${variety.context.slice(0, 160)}${variety.context.length > 160 ? '…' : ''}` : 'No context available';

              return (
                <div
                  key={variety._selectionKey}
                  className={`rounded-xl border transition ${
                    selected ? 'border-green-400 bg-green-50/40 shadow-sm' : 'border-gray-200 bg-white'
                  }`}
                >
                  <button
                    className="flex w-full items-center justify-between gap-4 px-4 py-3 text-left"
                    onClick={() => toggleSelection(variety._selectionKey)}
                  >
                    <div>
                      <div className="flex items-center gap-3">
                        <span
                          className={`flex h-6 w-6 items-center justify-center rounded-full border text-sm font-semibold ${
                            selected ? 'border-green-500 bg-green-500 text-white' : 'border-gray-300 text-gray-500'
                          }`}
                        >
                          {selected ? '✓' : ''}
                        </span>
                        <div>
                          <p className="text-base font-semibold text-gray-900">
                            {variety.variety_name || 'Unnamed Variety'}
                          </p>
                          <p className="text-xs uppercase tracking-wide text-gray-500">
                            {variety.crop_name}
                          </p>
                        </div>
                      </div>
                    </div>
                    <div className="flex items-center gap-3">
                      {renderConfidenceBadge(confidence)}
                      <ArrowRightCircle size={18} className="text-gray-400" />
                    </div>
                  </button>

                  <div className="grid gap-3 border-t border-gray-100 px-4 py-3 md:grid-cols-4">
                    <div>
                      <p className="text-xs font-semibold uppercase text-gray-500">Variety Type</p>
                      <p className="text-sm text-gray-700">{variety.variety_type || '—'}</p>
                    </div>
                    <div>
                      <p className="text-xs font-semibold uppercase text-gray-500">Yield Potential</p>
                      <p className="text-sm text-gray-700">{variety.yield_potential || '—'}</p>
                    </div>
                    <div>
                      <p className="text-xs font-semibold uppercase text-gray-500">Maturity Days</p>
                      <p className="text-sm text-gray-700">{variety.maturity_days ?? '—'}</p>
                    </div>
                    <div>
                      <p className="text-xs font-semibold uppercase text-gray-500">Source</p>
                      <p className="text-sm text-gray-700">{variety.source_document || '—'}</p>
                    </div>
                  </div>

                  <div className="border-t border-gray-100 px-4 py-3 text-sm text-gray-600">
                    <p className="mb-1 text-xs font-semibold uppercase text-gray-500">Context Preview</p>
                    <p>{previewContext}</p>
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        <div className="flex flex-col gap-3 border-t border-gray-200 bg-gray-50 px-6 py-4 md:flex-row md:items-center md:justify-between">
          <p className="text-sm text-gray-600">
            Selected varieties will be saved with <span className="font-medium text-gray-800">validated</span> status.
          </p>
          <div className="flex gap-3">
            <button
              onClick={onClose}
              className="rounded-lg border border-gray-300 px-4 py-2 text-sm text-gray-700 transition hover:bg-white"
              disabled={isSubmitting}
            >
              Cancel
            </button>
            <button
              onClick={handleSubmit}
              disabled={isSubmitting || selectedVarieties.length === 0}
              className={`flex items-center gap-2 rounded-lg px-4 py-2 text-sm font-semibold text-white transition ${
                isSubmitting || selectedVarieties.length === 0
                  ? 'bg-gray-400 cursor-not-allowed'
                  : 'bg-green-600 hover:bg-green-700'
              }`}
            >
              <ShieldCheck size={18} />
              {isSubmitting ? 'Saving...' : `Save ${selectedVarieties.length || ''} Varieties`}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default VarietyValidationModal;
