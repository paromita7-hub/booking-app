"use client";

import { useEffect, useState, useRef } from "react";
import { Header } from "@/components/Header";
import { api } from "@/lib/api";
import { IngestionLog, IngestionStatus, Property } from "@/types";
import {
  UploadCloud,
  FileSpreadsheet,
  FileCode,
  Download,
  ShieldCheck,
  ShieldAlert,
  CheckCircle,
  AlertCircle,
  Clock,
  RefreshCw,
} from "lucide-react";
import { formatDate } from "@/lib/utils";

export default function DataImportsPage() {
  const [status, setStatus] = useState<IngestionStatus | null>(null);
  const [history, setHistory] = useState<IngestionLog[]>([]);
  const [properties, setProperties] = useState<Property[]>([]);
  const [selectedPropId, setSelectedPropId] = useState<string>("");
  const [isDemoData, setIsDemoData] = useState<boolean>(true);
  const [uploading, setUploading] = useState<boolean>(false);
  const [uploadResult, setUploadResult] = useState<{
    status: string;
    records_processed: number;
    records_added: number;
    records_skipped: number;
    error_message?: string | null;
  } | null>(null);
  const [uploadError, setUploadError] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const loadData = () => {
    api.getIngestionStatus().then(setStatus).catch(console.error);
    api.getIngestionHistory().then(setHistory).catch(console.error);
    api.getProperties().then(setProperties).catch(console.error);
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setUploading(true);
    setUploadResult(null);
    setUploadError(null);

    try {
      const propId = selectedPropId ? parseInt(selectedPropId, 10) : undefined;
      const res = await api.uploadReviews(file, propId, isDemoData);
      setUploadResult(res);
      loadData();
    } catch (err: any) {
      setUploadError(err.message || "Failed to process and import file.");
    } finally {
      setUploading(false);
      if (fileInputRef.current) {
        fileInputRef.current.value = "";
      }
    }
  };

  const handleDownloadTemplate = () => {
    window.open("http://127.0.0.1:8000/api/reviews/template", "_blank");
  };

  return (
    <div className="flex-1 flex flex-col min-h-screen">
      <Header
        selectedPropertyId={null}
        onPropertyChange={() => {}}
      />

      <div className="p-8 space-y-8 max-w-7xl mx-auto w-full">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-slate-900">
            Data Collection & Ingestion Hub
          </h1>
          <p className="text-sm text-slate-500 mt-1">
            Import guest reviews via CSV/JSON exports, monitor collection safety modes, and inspect ingestion logs.
          </p>
        </div>

        {/* Collection Mode & Permission Status Banner */}
        <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm flex flex-col md:flex-row md:items-center justify-between gap-6">
          <div className="flex items-start gap-3">
            {status?.automated_scraping_enabled ? (
              <ShieldAlert size={28} className="text-amber-600 flex-shrink-0" />
            ) : (
              <ShieldCheck size={28} className="text-blue-800 flex-shrink-0" />
            )}
            <div>
              <div className="flex items-center gap-2">
                <span className="font-bold text-slate-900 text-base">
                  Current Collection Architecture: Safe Authorized Mode
                </span>
                <span className="text-[11px] font-semibold bg-emerald-100 text-emerald-800 px-2 py-0.5 rounded">
                  Policy Compliant
                </span>
              </div>
              <p className="text-xs text-slate-500 mt-1 max-w-2xl leading-relaxed">
                Automated live scraping is strictly disabled by default. The system operates via authorized CSV & JSON data imports with deterministic SHA-256 fingerprinting to prevent duplicates.
              </p>
            </div>
          </div>

          <div className="flex flex-col sm:flex-row items-center gap-3">
            <button
              onClick={handleDownloadTemplate}
              className="w-full sm:w-auto flex items-center justify-center gap-2 border border-slate-300 hover:bg-slate-50 text-slate-700 text-xs font-semibold px-4 py-2.5 rounded-lg transition shadow-sm"
            >
              <Download size={14} />
              <span>Download CSV Template</span>
            </button>
          </div>
        </div>

        {/* Upload Form Box */}
        <div className="bg-white p-8 rounded-xl border border-slate-200 shadow-sm space-y-6">
          <div className="border-b border-slate-100 pb-4">
            <h3 className="font-bold text-slate-900 text-base">Import Reviews File</h3>
            <p className="text-xs text-slate-500 mt-0.5">
              Supports standard Booking.com review export CSVs or structured JSON arrays.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1.5">
                Target Property (Optional):
              </label>
              <select
                value={selectedPropId}
                onChange={(e) => setSelectedPropId(e.target.value)}
                className="w-full py-2 px-3 text-xs border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white"
              >
                <option value="">Auto-detect from file columns (Recommended)</option>
                {properties.map((p) => (
                  <option key={p.id} value={p.id}>
                    Assign to: {p.name}
                  </option>
                ))}
              </select>
              <p className="text-[11px] text-slate-400 mt-1">
                If the file specifies property names, it will map them automatically.
              </p>
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1.5">
                Demo Tagging:
              </label>
              <label className="flex items-center gap-2 text-xs text-slate-700 mt-2 cursor-pointer">
                <input
                  type="checkbox"
                  checked={isDemoData}
                  onChange={(e) => setIsDemoData(e.target.checked)}
                  className="rounded border-slate-300 text-blue-600 focus:ring-blue-500"
                />
                <span>Tag imported records as DEMO dataset</span>
              </label>
              <p className="text-[11px] text-slate-400 mt-1">
                Ensures test or synthetic data is visibly segregated from genuine production reviews.
              </p>
            </div>
          </div>

          {/* Drag & Drop File Upload Zone */}
          <div
            onClick={() => fileInputRef.current?.click()}
            className={`border-2 border-dashed rounded-xl p-8 text-center cursor-pointer transition-colors ${
              uploading
                ? "border-blue-400 bg-blue-50/30"
                : "border-slate-300 hover:border-blue-600 hover:bg-slate-50/50"
            }`}
          >
            <input
              ref={fileInputRef}
              type="file"
              accept=".csv,.json"
              className="hidden"
              onChange={handleFileUpload}
              disabled={uploading}
            />
            <div className="flex flex-col items-center gap-2">
              <UploadCloud size={36} className="text-blue-700" />
              <div className="text-sm font-semibold text-slate-800">
                {uploading ? "Ingesting & Analyzing Reviews..." : "Click to select CSV or JSON file"}
              </div>
              <div className="text-xs text-slate-400">
                CSV (UTF-8) or JSON files up to 25MB
              </div>
            </div>
          </div>

          {/* Upload Status / Result Alert */}
          {uploadResult && (
            <div className="p-4 rounded-xl bg-emerald-50 border border-emerald-200 text-emerald-900 text-xs space-y-2">
              <div className="flex items-center gap-2 font-bold text-sm text-emerald-800">
                <CheckCircle size={16} />
                <span>Ingestion Completed Successfully!</span>
              </div>
              <div className="grid grid-cols-3 gap-2 text-center pt-2">
                <div className="bg-white p-2 rounded border border-emerald-200">
                  <div className="text-xs text-slate-500">Processed</div>
                  <div className="text-base font-bold text-slate-800">
                    {uploadResult.records_processed}
                  </div>
                </div>
                <div className="bg-white p-2 rounded border border-emerald-200">
                  <div className="text-xs text-emerald-700 font-semibold">Added (New)</div>
                  <div className="text-base font-bold text-emerald-700">
                    {uploadResult.records_added}
                  </div>
                </div>
                <div className="bg-white p-2 rounded border border-emerald-200">
                  <div className="text-xs text-amber-700 font-semibold">Skipped (Duplicates)</div>
                  <div className="text-base font-bold text-amber-700">
                    {uploadResult.records_skipped}
                  </div>
                </div>
              </div>
            </div>
          )}

          {uploadError && (
            <div className="p-4 rounded-xl bg-rose-50 border border-rose-200 text-rose-900 text-xs flex items-center gap-2">
              <AlertCircle size={16} className="text-rose-600 flex-shrink-0" />
              <span>{uploadError}</span>
            </div>
          )}
        </div>

        {/* Historical Ingestion Runs */}
        <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
          <div className="p-6 border-b border-slate-100 flex items-center justify-between">
            <div>
              <h3 className="font-bold text-slate-900 text-base">Ingestion History & Audit Log</h3>
              <p className="text-xs text-slate-500 mt-0.5">
                Audit trail of all imports, duplicate skips, and completion statuses.
              </p>
            </div>
            <button
              onClick={loadData}
              className="p-1.5 rounded-lg border border-slate-200 text-slate-500 hover:text-slate-800 hover:bg-slate-50"
              title="Refresh history"
            >
              <RefreshCw size={14} />
            </button>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse text-xs">
              <thead>
                <tr className="bg-slate-50 border-b border-slate-200 text-slate-500 font-semibold uppercase text-[10px] tracking-wider">
                  <th className="py-3 px-6">ID</th>
                  <th className="py-3 px-6">Source / File</th>
                  <th className="py-3 px-6">Target Property</th>
                  <th className="py-3 px-6">Status</th>
                  <th className="py-3 px-6 text-center">Processed</th>
                  <th className="py-3 px-6 text-center">Added</th>
                  <th className="py-3 px-6 text-center">Skipped</th>
                  <th className="py-3 px-6">Started At</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 text-slate-700">
                {history.length === 0 ? (
                  <tr>
                    <td colSpan={8} className="py-8 text-center text-slate-400">
                      No ingestion runs recorded yet.
                    </td>
                  </tr>
                ) : (
                  history.map((log) => (
                    <tr key={log.id} className="hover:bg-slate-50/50">
                      <td className="py-3.5 px-6 font-mono text-slate-400">#{log.id}</td>
                      <td className="py-3.5 px-6 font-medium text-slate-900">{log.source}</td>
                      <td className="py-3.5 px-6 text-slate-500">
                        {log.property_name || "Auto-detected"}
                      </td>
                      <td className="py-3.5 px-6">
                        <span
                          className={`px-2 py-0.5 rounded text-[10px] font-semibold uppercase tracking-wider ${
                            log.status === "completed"
                              ? "bg-emerald-100 text-emerald-800"
                              : log.status === "partial"
                              ? "bg-amber-100 text-amber-800"
                              : "bg-rose-100 text-rose-800"
                          }`}
                        >
                          {log.status}
                        </span>
                      </td>
                      <td className="py-3.5 px-6 text-center font-semibold">
                        {log.records_processed}
                      </td>
                      <td className="py-3.5 px-6 text-center text-emerald-700 font-semibold">
                        +{log.records_added}
                      </td>
                      <td className="py-3.5 px-6 text-center text-amber-700 font-semibold">
                        {log.records_skipped}
                      </td>
                      <td className="py-3.5 px-6 text-slate-400">
                        {new Date(log.started_at).toLocaleString("en-AU", {
                          timeZone: "Australia/Sydney",
                          dateStyle: "short",
                          timeStyle: "short",
                        })}
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
}
