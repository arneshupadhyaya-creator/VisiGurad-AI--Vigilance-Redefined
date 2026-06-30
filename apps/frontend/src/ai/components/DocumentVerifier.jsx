import React, { useState, useRef } from 'react';
import { verifyDocument } from '../services/aiClient';
import { 
  UploadCloud, File, AlertTriangle, ShieldCheck, ShieldAlert, 
  Trash2, RefreshCw, Loader2, Sparkles, HelpCircle 
} from 'lucide-react';

/**
 * DocumentVerifier Component
 * Purpose: Drag & drop interface for verifying document authenticity using local AI models.
 * Responsibility: File validations, upload progress, state displays, and result visualization.
 */
export const DocumentVerifier = () => {
  const [file, setFile] = useState(null);
  const [previewUrl, setPreviewUrl] = useState('');
  const [dragActive, setDragActive] = useState(false);
  const [progress, setProgress] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [result, setResult] = useState(null);

  const fileInputRef = useRef(null);

  const validateFile = (selectedFile) => {
    setError('');
    setResult(null);

    const allowedMimes = ['image/jpeg', 'image/jpg', 'image/png', 'image/tiff', 'application/pdf'];
    const fileExt = selectedFile.name.split('.').pop().toLowerCase();
    const allowedExts = ['pdf', 'png', 'jpg', 'jpeg', 'tiff'];

    if (!allowedMimes.includes(selectedFile.type) && !allowedExts.includes(fileExt)) {
      setError('Unsupported file type. Allowed: PDF, PNG, JPG, JPEG, TIFF.');
      return false;
    }

    if (selectedFile.size > 10 * 1024 * 1024) {
      setError('File size exceeds the 10MB upload threshold.');
      return false;
    }

    return true;
  };

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const selected = e.dataTransfer.files[0];
      if (validateFile(selected)) {
        setFile(selected);
        if (selected.type.startsWith('image/')) {
          setPreviewUrl(URL.createObjectURL(selected));
        } else {
          setPreviewUrl('');
        }
      }
    }
  };

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      const selected = e.target.files[0];
      if (validateFile(selected)) {
        setFile(selected);
        if (selected.type.startsWith('image/')) {
          setPreviewUrl(URL.createObjectURL(selected));
        } else {
          setPreviewUrl('');
        }
      }
    }
  };

  const handleUploadSubmit = async () => {
    if (!file) return;

    setLoading(true);
    setProgress(0);
    setError('');
    setResult(null);

    try {
      const response = await verifyDocument(file, (percent) => {
        setProgress(percent);
      });
      if (response.status === 'success') {
        setResult(response.data);
      } else {
        setError('Verification failed. Unexpected response payload.');
      }
    } catch (err) {
      setError(err.response?.data?.error || err.message || 'AI verification offline or timed out.');
    } finally {
      setLoading(false);
    }
  };

  const resetVerifier = () => {
    setFile(null);
    setPreviewUrl('');
    setProgress(0);
    setResult(null);
    setError('');
  };

  return (
    <div className="space-y-6 text-left">
      <div>
        <h2 className="text-xl font-bold text-white flex items-center gap-2">
          <Sparkles className="w-5 h-5 text-indigo-400" />
          Local AI Document Authenticity Checker
        </h2>
        <p className="text-zinc-400 text-xs mt-1">
          Scans document layers and compression parameters locally to check for digital alteration, tampering, or AI-generated copy.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
        {/* Upload Interface Panel */}
        <div className="lg:col-span-7 space-y-4">
          {!file && (
            <div
              onDragEnter={handleDrag}
              onDragOver={handleDrag}
              onDragLeave={handleDrag}
              onDrop={handleDrop}
              onClick={() => fileInputRef.current.click()}
              className={`relative border-2 border-dashed rounded-2xl p-12 text-center cursor-pointer transition-all duration-300 ${
                dragActive
                  ? 'border-indigo-500 bg-indigo-500/5 shadow-[0_0_20px_rgba(99,102,241,0.15)]'
                  : 'border-zinc-800 hover:border-zinc-700 bg-zinc-900/10'
              }`}
            >
              <input
                type="file"
                ref={fileInputRef}
                className="hidden"
                onChange={handleFileChange}
                accept=".pdf,.png,.jpg,.jpeg,.tiff,image/jpeg,image/png,image/tiff,application/pdf"
              />
              <div className="space-y-4">
                <div className="mx-auto w-14 h-14 rounded-xl bg-zinc-900 border border-zinc-800 flex items-center justify-center">
                  <UploadCloud className="w-8 h-8 text-indigo-400" />
                </div>
                <div>
                  <span className="text-white font-semibold">Click to upload document</span> or drag & drop
                  <p className="text-zinc-500 text-xs mt-1">PDF, PNG, JPG, JPEG, TIFF (Max 10MB)</p>
                </div>
              </div>
            </div>
          )}

          {error && (
            <div className="p-4 bg-rose-500/10 border border-rose-500/20 text-rose-450 rounded-xl text-xs flex items-center gap-2">
              <AlertTriangle className="w-4 h-4 flex-shrink-0 animate-bounce" />
              <span>{error}</span>
            </div>
          )}

          {file && (
            <div className="bg-zinc-900/30 border border-zinc-800 rounded-2xl p-5 space-y-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className="p-2.5 bg-zinc-950 border border-zinc-800 rounded-xl">
                    <File className="w-6 h-6 text-indigo-400" />
                  </div>
                  <div>
                    <h4 className="text-sm font-semibold text-white truncate max-w-[280px]">{file.name}</h4>
                    <p className="text-zinc-500 text-xs">{(file.size / (1024 * 1024)).toFixed(2)} MB</p>
                  </div>
                </div>
                {!loading && (
                  <button
                    onClick={resetVerifier}
                    className="p-2 hover:bg-zinc-800 text-zinc-500 hover:text-rose-400 rounded-lg transition-colors cursor-pointer"
                    title="Remove File"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                )}
              </div>

              {/* Progress bar */}
              {loading && (
                <div className="space-y-2">
                  <div className="flex justify-between text-xs text-zinc-400">
                    <span className="flex items-center gap-1.5 animate-pulse">
                      <Loader2 className="w-3.5 h-3.5 text-indigo-500 animate-spin" />
                      Uploading document payload...
                    </span>
                    <span>{progress}%</span>
                  </div>
                  <div className="h-1.5 w-full bg-zinc-950 rounded-full overflow-hidden border border-zinc-900">
                    <div
                      className="h-full bg-indigo-500 transition-all duration-300"
                      style={{ width: `${progress}%` }}
                    ></div>
                  </div>
                </div>
              )}

              {/* Image Preview Container */}
              {previewUrl && (
                <div className="relative aspect-video rounded-xl overflow-hidden border border-zinc-800 bg-zinc-950 flex items-center justify-center">
                  <img
                    src={previewUrl}
                    alt="Uploaded preview"
                    className="max-h-full max-w-full object-contain"
                  />
                  {/* Highlight suspicious areas overlay if tampering detected */}
                  {result && result.tampering_detected && result.suspicious_regions && (
                    <div className="absolute inset-0 pointer-events-none">
                      {result.suspicious_regions.map((region, idx) => (
                        <div
                          key={idx}
                          className="absolute border-2 border-dashed border-rose-500 bg-rose-500/10 shadow-[0_0_10px_rgba(239,68,68,0.4)] animate-pulse"
                          style={{
                            left: `${region.x / 8}%`,
                            top: `${region.y / 8}%`,
                            width: `${region.width / 4}%`,
                            height: `${region.height / 4}%`
                          }}
                          title={region.reason}
                        />
                      ))}
                    </div>
                  )}
                </div>
              )}

              {!loading && !result && (
                <button
                  onClick={handleUploadSubmit}
                  className="w-full py-3 bg-indigo-600 hover:bg-indigo-700 text-white font-semibold text-xs rounded-xl shadow-[0_0_15px_rgba(99,102,241,0.2)] transition-all cursor-pointer flex items-center justify-center gap-2"
                >
                  <Sparkles className="w-4 h-4" />
                  Request AI Verification Analysis
                </button>
              )}
            </div>
          )}
        </div>

        {/* Results Metadata Display (5 cols) */}
        <div className="lg:col-span-5">
          {result ? (
            <div className="bg-zinc-900/30 border border-zinc-800 rounded-2xl p-6 space-y-6">
              <div className="flex items-center gap-2.5 pb-4 border-b border-zinc-800">
                {result.tampering_detected ? (
                  <div className="p-2 bg-rose-500/10 border border-rose-500/20 text-rose-400 rounded-xl">
                    <ShieldAlert className="w-6 h-6" />
                  </div>
                ) : (
                  <div className="p-2 bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 rounded-xl">
                    <ShieldCheck className="w-6 h-6" />
                  </div>
                )}
                <div>
                  <h3 className="font-bold text-white text-sm">
                    {result.tampering_detected ? 'Tampering Anomalies Detected' : 'Authenticity Verified'}
                  </h3>
                  <p className="text-zinc-550 text-xs">Analysis status: {result.authenticity ? 'Verified Genuine' : 'Suspicious Document'}</p>
                </div>
              </div>

              {/* Confidence & Risk Score */}
              <div className="grid grid-cols-2 gap-4">
                <div className="p-3.5 bg-zinc-950 rounded-xl border border-zinc-800">
                  <span className="text-[10px] font-semibold text-zinc-500 uppercase tracking-widest block mb-0.5">Confidence</span>
                  <span className={`text-xl font-extrabold ${result.tampering_detected ? 'text-rose-400' : 'text-emerald-400'}`}>
                    {result.confidence}%
                  </span>
                </div>
                <div className="p-3.5 bg-zinc-950 rounded-xl border border-zinc-800">
                  <span className="text-[10px] font-semibold text-zinc-500 uppercase tracking-widest block mb-0.5">Risk Rating</span>
                  <span className={`text-xl font-extrabold ${result.risk_score > 0.4 ? 'text-rose-450' : 'text-emerald-450'}`}>
                    {result.risk_score}
                  </span>
                </div>
              </div>

              {/* Explanations list */}
              <div className="space-y-2">
                <h4 className="text-xs font-bold text-zinc-400 uppercase tracking-wider">AI Forensic Log</h4>
                <ul className="space-y-1.5">
                  {result.explanation.map((exp, idx) => (
                    <li key={idx} className="text-xs text-zinc-450 flex items-start gap-1.5">
                      <span className="text-indigo-400 mt-1">•</span>
                      <span>{exp}</span>
                    </li>
                  ))}
                </ul>
              </div>

              {/* Metadata Details */}
              {result.metadata_analysis && (
                <div className="border-t border-zinc-800 pt-4 space-y-2.5">
                  <h4 className="text-xs font-bold text-zinc-400 uppercase tracking-wider">Metadata Signatures</h4>
                  <div className="space-y-1.5 font-mono text-[10px] text-zinc-500">
                    {Object.entries(result.metadata_analysis).map(([key, val]) => (
                      <div key={key} className="flex justify-between">
                        <span>{key}:</span>
                        <span className="text-zinc-300 truncate max-w-[180px]">{val.toString()}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {result.tampering_detected && (
                <button
                  onClick={resetVerifier}
                  className="w-full py-2.5 bg-zinc-950 border border-zinc-800 hover:border-zinc-700 text-zinc-350 text-xs font-semibold rounded-lg transition-colors cursor-pointer flex items-center justify-center gap-1.5"
                >
                  <RefreshCw className="w-3.5 h-3.5" />
                  Reset Work Environment
                </button>
              )}
            </div>
          ) : (
            <div className="bg-zinc-900/10 border border-zinc-850 border-dashed rounded-2xl p-8 text-center text-zinc-550 text-xs h-full flex flex-col items-center justify-center gap-3 py-16">
              <ShieldCheck className="w-8 h-8 text-zinc-800" />
              <p className="max-w-[220px] leading-relaxed">Upload a document file to trigger automated AI signature validations and tamper sweeps.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
