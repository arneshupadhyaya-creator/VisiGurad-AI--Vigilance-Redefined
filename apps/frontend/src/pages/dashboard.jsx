import React, { useState, useEffect, useRef } from 'react';
import { useAuth } from '../hooks/useAuth';
import { 
  uploadAndAnalyze, fetchScanHistory, deleteScanRecord 
} from '../services/scanService';
import { triggerAIModelCall } from '../services/ai/aiService';
import { 
  UploadCloud, ShieldCheck, ShieldAlert, History, 
  Trash2, FileImage, Loader2, Play, ExternalLink, RefreshCw,
  User, Database, Cpu, Activity
} from 'lucide-react';
import Navbar from '../components/navbar.jsx';
import Footer from '../components/footer.jsx';

// Server URL for serving images statically
const SERVER_URL = 'http://localhost:5000';

/**
 * Dashboard Component
 * The main forensic work environment. Fully integrated with AuthContext and modular services.
 */
const Dashboard = () => {
  const { user } = useAuth();
  
  // State Hooks
  const [file, setFile] = useState(null);
  const [previewUrl, setPreviewUrl] = useState('');
  const [dragActive, setDragActive] = useState(false);
  const [loading, setLoading] = useState(false);
  const [loadingMessage, setLoadingMessage] = useState('Initiating forensic sweep...');
  const [scanResult, setScanResult] = useState(null);
  const [history, setHistory] = useState([]);
  const [error, setError] = useState('');
  const [warningMsg, setWarningMsg] = useState('');
  
  // AI and System logs state placeholders
  const [aiMetric, setAiMetric] = useState(null);
  const [activeTab, setActiveTab] = useState('upload'); // upload | logs | ai
  
  const fileInputRef = useRef(null);
  
  // Loading status messages to rotate through during analysis
  const loadingStages = [
    'Parsing document metadata...',
    'Resaving image under delta quality settings...',
    'Evaluating compression divergence...',
    'Isolating modification hotspots...',
    'Rendering Error Level Analysis (ELA) map...'
  ];

  // Fetch scan history from database on mount
  useEffect(() => {
    loadHistory();
  }, []);

  // Cycle loading messages when processing files
  useEffect(() => {
    let interval;
    if (loading) {
      let stageIndex = 0;
      interval = setInterval(() => {
        setLoadingMessage(loadingStages[stageIndex]);
        stageIndex = (stageIndex + 1) % loadingStages.length;
      }, 1500);
    }
    return () => clearInterval(interval);
  }, [loading]);

  const loadHistory = async () => {
    try {
      const data = await fetchScanHistory();
      setHistory(data);
    } catch (err) {
      console.error('Error fetching scan history:', err);
    }
  };

  // Handle drag events
  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  // Handle drop events
  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      validateAndSetFile(e.dataTransfer.files[0]);
    }
  };

  // Handle manual file selection
  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      validateAndSetFile(e.target.files[0]);
    }
  };

  const validateAndSetFile = (selectedFile) => {
    setError('');
    const validTypes = ['image/jpeg', 'image/jpg', 'image/png'];
    if (!validTypes.includes(selectedFile.type)) {
      setError('Invalid file type. Please upload a JPEG or PNG image.');
      return;
    }
    if (selectedFile.size > 10 * 1024 * 1024) {
      setError('File size too large. Maximum size allowed is 10MB.');
      return;
    }

    setFile(selectedFile);
    setPreviewUrl(URL.createObjectURL(selectedFile));
    setScanResult(null);
  };

  // Submit scan to backend
  const handleScanSubmit = async (e) => {
    e.preventDefault();
    if (!file) return;

    setLoading(true);
    setError('');
    setWarningMsg('');
    setScanResult(null);

    try {
      const data = await uploadAndAnalyze(file);
      setScanResult(data.scan);
      if (data.warning) {
        setWarningMsg(data.warning);
      }
      
      // Auto trigger a mock AI inference check to populate the AI placeholder metrics
      const aiResult = await triggerAIModelCall(data.scan._id);
      setAiMetric(aiResult);
      
      // Refresh persistent MongoDB logs
      loadHistory();
    } catch (err) {
      setError(err.response?.data?.error || 'Error processing scan. Please verify backend state.');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  // Delete scan history item
  const handleDeleteScan = async (id) => {
    try {
      await deleteScanRecord(id);
      setHistory(history.filter(item => item._id !== id));
      if (scanResult && scanResult._id === id) {
        setScanResult(null);
        setFile(null);
        setPreviewUrl('');
      }
    } catch (err) {
      console.error('Error deleting scan:', err);
    }
  };

  // Load a historical scan back into active viewing screen
  const viewHistoricalScan = (scan) => {
    setScanResult(scan);
    setPreviewUrl(`${SERVER_URL}${scan.originalPath}`);
    setFile(null);
    setError('');
    setWarningMsg(scan.dbOffline ? 'Running on database offline fallback' : '');
  };

  // Reset work environment
  const resetDashboard = () => {
    setFile(null);
    setPreviewUrl('');
    setScanResult(null);
    setError('');
    setWarningMsg('');
  };

  // Get color configurations depending on threat levels
  const getThreatMeta = (score, status) => {
    if (status === 'Clean' || score < 15) {
      return {
        color: 'text-emerald-400',
        bg: 'bg-emerald-500/10 border-emerald-500/20',
        bar: 'bg-emerald-500',
        text: 'Document integrity appears high. No obvious compression anomalies detected.'
      };
    } else if (status === 'Suspicious' || score < 45) {
      return {
        color: 'text-amber-400',
        bg: 'bg-amber-500/10 border-amber-500/20',
        bar: 'bg-amber-500',
        text: 'Minor compression irregularities detected. May contain light retouching or scaling.'
      };
    } else {
      return {
        color: 'text-rose-500',
        bg: 'bg-rose-500/10 border-rose-500/20',
        bar: 'bg-rose-500',
        text: 'Critical compression anomalies detected. Heavy visual edit hotspots identified.'
      };
    }
  };

  return (
    <div className="bg-zinc-950 min-h-screen text-zinc-100 flex flex-col font-sans">
      <Navbar />

      <main className="flex-grow max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-28 pb-16 w-full space-y-8">
        
        {/* welcome panel & user card */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="md:col-span-2 bg-zinc-900/40 border border-zinc-800/80 rounded-2xl p-6 flex flex-col justify-between text-left">
            <div>
              <h1 className="text-2xl font-bold text-white">Welcome back, {user?.email?.split('@')[0]}</h1>
              <p className="text-zinc-400 text-sm mt-1">Sovereign workspace interface. Your forensic security token is authenticated.</p>
            </div>
            <div className="flex gap-3 mt-6">
              <button 
                onClick={() => setActiveTab('upload')}
                className={`px-4 py-2 text-xs font-semibold rounded-lg border transition-all cursor-pointer ${
                  activeTab === 'upload' 
                    ? 'bg-indigo-600 border-indigo-650 text-white shadow-md' 
                    : 'bg-zinc-950 border-zinc-800 hover:border-zinc-700 text-zinc-400 hover:text-white'
                }`}
              >
                Upload Sandbox
              </button>
              <button 
                onClick={() => setActiveTab('logs')}
                className={`px-4 py-2 text-xs font-semibold rounded-lg border transition-all cursor-pointer ${
                  activeTab === 'logs' 
                    ? 'bg-indigo-600 border-indigo-650 text-white shadow-md' 
                    : 'bg-zinc-950 border-zinc-800 hover:border-zinc-700 text-zinc-400 hover:text-white'
                }`}
              >
                Auditor Logs Placeholder
              </button>
              <button 
                onClick={() => setActiveTab('ai')}
                className={`px-4 py-2 text-xs font-semibold rounded-lg border transition-all cursor-pointer ${
                  activeTab === 'ai' 
                    ? 'bg-indigo-600 border-indigo-650 text-white shadow-md' 
                    : 'bg-zinc-950 border-zinc-800 hover:border-zinc-700 text-zinc-400 hover:text-white'
                }`}
              >
                AI Model Integration contract
              </button>
            </div>
          </div>

          {/* User Info Card */}
          <div className="bg-zinc-900/40 border border-zinc-800/80 rounded-2xl p-6 text-left space-y-4">
            <h3 className="text-xs font-bold text-zinc-500 uppercase tracking-wider flex items-center gap-1.5">
              <User className="w-4 h-4 text-indigo-400" />
              Active Auditor profile
            </h3>
            <div className="space-y-2">
              <div className="flex justify-between text-xs">
                <span className="text-zinc-500">ID:</span>
                <span className="font-mono text-zinc-300">{user?.id?.slice(-8) || 'DUMMY_ID'}</span>
              </div>
              <div className="flex justify-between text-xs">
                <span className="text-zinc-500">Role:</span>
                <span className="text-zinc-300 font-semibold">{user?.role || 'Security_Auditor'}</span>
              </div>
              <div className="flex justify-between text-xs">
                <span className="text-zinc-500">Authentication:</span>
                <span className="text-emerald-400 flex items-center gap-1">
                  <div className="w-1.5 h-1.5 rounded-full bg-emerald-450 animate-ping"></div>
                  Bearer JWT Active
                </span>
              </div>
            </div>
          </div>
        </div>

        {/* Tab 1: Upload Sandbox */}
        {activeTab === 'upload' && (
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
            
            {/* Left Block: Upload & Preview Visualizer (8 cols) */}
            <div className="lg:col-span-8 space-y-6">
              
              {!previewUrl && (
                <div 
                  onDragEnter={handleDrag}
                  onDragOver={handleDrag}
                  onDragLeave={handleDrag}
                  onDrop={handleDrop}
                  onClick={() => fileInputRef.current.click()}
                  className={`relative border-2 border-dashed rounded-2xl p-12 text-center cursor-pointer transition-all duration-300 ${
                    dragActive 
                      ? 'border-indigo-500 bg-indigo-500/5 shadow-[0_0_25px_rgba(79,70,229,0.1)]' 
                      : 'border-zinc-800 hover:border-zinc-700 bg-zinc-900/10'
                  }`}
                >
                  <input 
                    type="file" 
                    ref={fileInputRef}
                    className="hidden" 
                    onChange={handleFileChange}
                    accept="image/jpeg,image/png,image/jpg"
                  />
                  
                  <div className="space-y-4">
                    <div className="mx-auto w-14 h-14 rounded-xl bg-zinc-900 border border-zinc-800 flex items-center justify-center text-zinc-400">
                      <UploadCloud className="w-8 h-8 text-indigo-400" />
                    </div>
                    <div>
                      <span className="text-white font-semibold">Click to upload</span> or drag and drop
                      <p className="text-zinc-500 text-xs mt-1.5">JPEG, JPG, or PNG (Max 10MB)</p>
                    </div>
                  </div>
                </div>
              )}

              {error && (
                <div className="p-4 bg-rose-500/10 border border-rose-500/20 text-rose-400 rounded-xl text-sm flex items-center gap-2">
                  <ShieldAlert className="w-5 h-5 flex-shrink-0" />
                  <span>{error}</span>
                </div>
              )}

              {warningMsg && (
                <div className="p-4 bg-amber-500/10 border border-amber-500/20 text-amber-400 rounded-xl text-xs flex items-center gap-2">
                  <ShieldAlert className="w-4 h-4 flex-shrink-0" />
                  <span>{warningMsg}</span>
                </div>
              )}

              {loading && (
                <div className="bg-zinc-900/40 border border-zinc-800/80 rounded-2xl p-16 text-center space-y-4 flex flex-col items-center justify-center">
                  <Loader2 className="w-10 h-10 text-indigo-500 animate-spin" />
                  <div className="space-y-1.5">
                    <h4 className="text-white font-semibold text-sm">Forensic Check In Progress</h4>
                    <p className="text-zinc-500 text-xs animate-pulse">{loadingMessage}</p>
                  </div>
                </div>
              )}

              {previewUrl && !loading && (
                <div className="bg-zinc-900/20 border border-zinc-850 rounded-2xl p-6 space-y-6">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div className="space-y-2 text-left">
                      <div className="text-xs font-semibold text-zinc-400 flex items-center gap-1.5">
                        <FileImage className="w-3.5 h-3.5" />
                        Original Document / Image
                      </div>
                      <div className="bg-zinc-950 rounded-xl border border-zinc-900/80 overflow-hidden flex items-center justify-center aspect-video relative group">
                        <img 
                          src={previewUrl} 
                          alt="Original Upload" 
                          className="max-h-full max-w-full object-contain"
                        />
                      </div>
                    </div>

                    <div className="space-y-2 text-left">
                      <div className="text-xs font-semibold text-zinc-400 flex items-center gap-1.5">
                        <ShieldCheck className="w-3.5 h-3.5 text-indigo-400" />
                        Error Level Analysis (ELA) Map
                      </div>
                      <div className="bg-zinc-950 rounded-xl border border-zinc-900/80 overflow-hidden flex items-center justify-center aspect-video relative">
                        {scanResult ? (
                          <img 
                            src={`${SERVER_URL}${scanResult.elaPath}`} 
                            alt="ELA Map" 
                            className="max-h-full max-w-full object-contain"
                          />
                        ) : (
                          <div className="text-zinc-650 text-xs text-center flex flex-col items-center justify-center gap-2 p-4">
                            <Play className="w-8 h-8 text-zinc-800" />
                            Ready for forensic evaluation. Click 'Run Analysis'.
                          </div>
                        )}
                      </div>
                    </div>
                  </div>

                  {file && !scanResult && (
                    <div className="flex flex-col sm:flex-row items-center justify-between gap-4 pt-4 border-t border-zinc-900">
                      <div className="text-left w-full sm:w-auto">
                        <div className="text-sm font-semibold text-white truncate max-w-[320px]">{file.name}</div>
                        <div className="text-xs text-zinc-550 mt-0.5">{(file.size / (1024 * 1024)).toFixed(2)} MB</div>
                      </div>
                      <button 
                        onClick={handleScanSubmit}
                        className="w-full sm:w-auto flex items-center justify-center gap-2 px-6 py-3 bg-indigo-650 hover:bg-indigo-600 text-white font-semibold text-sm rounded-xl transition-all shadow-[0_0_15px_rgba(79,70,229,0.2)] cursor-pointer active:scale-95"
                      >
                        <Play className="w-4 h-4 fill-white" />
                        Run Forensic Analysis
                      </button>
                    </div>
                  )}

                  {scanResult && (
                    <div className="flex justify-end pt-4 border-t border-zinc-900">
                      <button 
                        onClick={resetDashboard}
                        className="flex items-center gap-1.5 px-4 py-2 bg-zinc-900 border border-zinc-800 hover:bg-zinc-800 text-zinc-350 text-xs font-semibold rounded-lg transition-colors cursor-pointer"
                      >
                        <RefreshCw className="w-3.5 h-3.5" />
                        Clear Sandbox
                      </button>
                    </div>
                  )}
                </div>
              )}
            </div>

            {/* Right Block: Gauge Report & Storage Guide (4 cols) */}
            <div className="lg:col-span-4 space-y-6">
              
              {scanResult ? (
                (() => {
                  const meta = getThreatMeta(scanResult.threatScore, scanResult.status);
                  return (
                    <div className="bg-zinc-900/25 border border-zinc-850 rounded-2xl p-6 text-left space-y-6">
                      <h3 className="text-lg font-bold text-white">Forensic Assessment</h3>
                      
                      <div className="space-y-2">
                        <div className="flex justify-between items-baseline">
                          <span className="text-xs text-zinc-400 font-semibold uppercase tracking-wider">Tamper Index</span>
                          <span className={`text-3xl font-extrabold ${meta.color}`}>{scanResult.threatScore}%</span>
                        </div>
                        <div className="h-2 w-full bg-zinc-950 rounded-full overflow-hidden border border-zinc-900">
                          <div 
                            className={`h-full ${meta.bar} transition-all duration-1000`} 
                            style={{ width: `${scanResult.threatScore}%` }}
                          ></div>
                        </div>
                      </div>

                      <div className={`p-4 rounded-xl border ${meta.bg} space-y-1.5`}>
                        <div className="flex items-center gap-2 font-bold text-sm">
                          {scanResult.status === 'Clean' ? (
                            <ShieldCheck className="w-5 h-5 text-emerald-400" />
                          ) : (
                            <ShieldAlert className="w-5 h-5 text-rose-500" />
                          )}
                          <span>Audit Status: {scanResult.status}</span>
                        </div>
                        <p className="text-xs text-zinc-400 leading-relaxed">
                          {meta.text}
                        </p>
                      </div>

                      <div className="border-t border-zinc-900 pt-4 space-y-2.5 text-xs text-zinc-500">
                        <div className="flex justify-between">
                          <span>File Name:</span>
                          <span className="text-zinc-400 truncate max-w-[150px]">{scanResult.originalName}</span>
                        </div>
                        <div className="flex justify-between">
                          <span>Original Size:</span>
                          <span className="text-zinc-400">{(scanResult.fileSize / 1024).toFixed(1)} KB</span>
                        </div>
                      </div>
                    </div>
                  );
                })()
              ) : (
                <div className="bg-zinc-900/15 border border-zinc-850 rounded-2xl p-6 text-center text-zinc-500 text-xs py-12">
                  <ShieldCheck className="w-8 h-8 mx-auto text-zinc-800 mb-2.5" />
                  Upload a document and initiate ELA to display real-time threat scores, tamper ratings, and audit records.
                </div>
              )}

              {/* Document Upload System Storage Placeholder */}
              <div className="bg-zinc-900/25 border border-zinc-850 rounded-2xl p-6 text-left space-y-4">
                <h3 className="text-sm font-bold text-white flex items-center gap-2">
                  <Database className="w-4 h-4 text-indigo-400" />
                  Storage Abstraction Layer
                </h3>
                <div className="space-y-3 text-xs text-zinc-400">
                  <div className="p-3 bg-zinc-950 rounded-xl border border-zinc-900 space-y-1">
                    <div className="font-semibold text-white">Active Driver: LocalStorage</div>
                    <p className="text-[11px] text-zinc-500 leading-relaxed">Uploads reside in apps/backend/uploads/ statically exposed by Express.</p>
                  </div>
                  <div className="p-3 bg-zinc-950/40 rounded-xl border border-dashed border-zinc-800 space-y-1 opacity-70">
                    <div className="font-semibold text-zinc-350">AWS S3 / Azure Blob [Decoupled]</div>
                    <p className="text-[11px] text-zinc-650 leading-relaxed">System architecture contains abstract StorageProvider drivers prepared for cloud migrations.</p>
                  </div>
                </div>
              </div>

            </div>

          </div>
        )}

        {/* Tab 2: Activity Monitoring Logs */}
        {activeTab === 'logs' && (
          <div className="bg-zinc-900/40 border border-zinc-800/80 rounded-2xl p-6 text-left space-y-6">
            <div className="flex items-center gap-2.5 border-b border-zinc-900 pb-4 justify-between">
              <div className="flex items-center gap-2">
                <Activity className="w-5 h-5 text-indigo-400" />
                <div>
                  <h3 className="text-lg font-bold text-white">Security Event Monitoring Service</h3>
                  <p className="text-zinc-500 text-xs mt-0.5 font-normal">Real-time application audit trail. Configured fallback: Logs saved to MongoDB AuditLogs collection.</p>
                </div>
              </div>
            </div>
            
            <div className="space-y-4 max-w-4xl">
              <div className="p-4 bg-zinc-950 rounded-xl border border-zinc-900 flex gap-4 items-start">
                <div className="p-2 bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 rounded-lg text-xs font-mono font-semibold">SUCCESS</div>
                <div className="space-y-1">
                  <div className="text-xs font-semibold text-white">USER_LOGIN_SUCCESS</div>
                  <p className="text-xs text-zinc-400">Auditor {user?.email} logged in. Session JWT token successfully issued.</p>
                  <span className="text-[10px] text-zinc-650">Timestamp: {new Date().toLocaleTimeString()}</span>
                </div>
              </div>
              
              <div className="p-4 bg-zinc-950 rounded-xl border border-zinc-900 flex gap-4 items-start">
                <div className="p-2 bg-indigo-500/10 border border-indigo-500/20 text-indigo-400 rounded-lg text-xs font-mono font-semibold">EVENT</div>
                <div className="space-y-1">
                  <div className="text-xs font-semibold text-white">FILE_UPLOADED / SCAN_CREATED</div>
                  <p className="text-xs text-zinc-400">Forensic file processed through LocalStorageProvider. Metadata saved to scans schema.</p>
                  <span className="text-[10px] text-zinc-650">Compliance Log ID: audit_evt_{user?.id?.slice(-5)}</span>
                </div>
              </div>

              <div className="p-4 bg-zinc-950/40 rounded-xl border border-dashed border-zinc-850 flex gap-4 items-start opacity-70">
                <div className="p-2 bg-purple-500/10 border border-purple-500/20 text-purple-400 rounded-lg text-xs font-mono font-semibold">COMPLIANCE</div>
                <div className="space-y-1">
                  <div className="text-xs font-semibold text-zinc-350">Event Collector Hook Details</div>
                  <p className="text-xs text-zinc-500 leading-relaxed">Events pipeline collects IP Address, User Agents, session flags, and computational outputs. Integrates directly into database audit collections for regulatory requirements.</p>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Tab 3: AI Integration Contract */}
        {activeTab === 'ai' && (
          <div className="bg-zinc-900/40 border border-zinc-800/80 rounded-2xl p-6 text-left space-y-6">
            <div className="flex items-center gap-2 border-b border-zinc-900 pb-4">
              <Cpu className="w-5 h-5 text-indigo-400" />
              <div>
                <h3 className="text-lg font-bold text-white">AI Model Integration Contract Framework</h3>
                <p className="text-zinc-500 text-xs mt-0.5">SaaS contract definition for future pluggable local deep learning models.</p>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-8 items-start">
              <div className="space-y-4">
                <h4 className="text-xs font-bold text-zinc-400 uppercase tracking-widest">Expected API Call Request Contract</h4>
                <div className="bg-zinc-950 rounded-xl p-4 border border-zinc-900 font-mono text-xs text-zinc-450 space-y-1.5 overflow-x-auto">
                  <div>{`{`}</div>
                  <div className="pl-4">"imagePath": <span className="text-indigo-400">"apps/backend/uploads/image.png"</span>,</div>
                  <div className="pl-4">"outputPath": <span className="text-indigo-400">"apps/backend/uploads/ela-image.png"</span>,</div>
                  <div className="pl-4">"options": {`{`}</div>
                  <div className="pl-8">"quality": <span className="text-purple-400">90</span>,</div>
                  <div className="pl-8">"channels": <span className="text-indigo-400">"RGB"</span></div>
                  <div className="pl-4">{`}`}</div>
                  <div>{`}`}</div>
                </div>
                <p className="text-xs text-zinc-550 leading-relaxed">Contract enforced on the backend via Zod validation libraries prior to spawning AI python wrappers.</p>
              </div>

              <div className="space-y-4">
                <h4 className="text-xs font-bold text-zinc-400 uppercase tracking-widest">Expected Model Response Contract</h4>
                <div className="bg-zinc-950 rounded-xl p-4 border border-zinc-900 font-mono text-xs text-zinc-450 space-y-1.5 overflow-x-auto">
                  <div>{`{`}</div>
                  <div className="pl-4">"success": <span className="text-emerald-405">true</span>,</div>
                  <div className="pl-4">"threatScore": <span className="text-purple-400">{aiMetric ? aiMetric.threatScore : '42.8'}</span>,</div>
                  <div className="pl-4">"status": <span className="text-indigo-400">"{aiMetric ? aiMetric.status : 'Suspicious'}"</span>,</div>
                  <div className="pl-4">"anomaliesCount": <span className="text-purple-400">{aiMetric ? aiMetric.anomaliesCount : '3'}</span>,</div>
                  <div className="pl-4">"modelName": <span className="text-indigo-400">"{aiMetric ? aiMetric.modelName : 'VisiGuardResNet50'}"</span>,</div>
                  <div className="pl-4">"simulated": <span className="text-emerald-405">true</span></div>
                  <div>{`}`}</div>
                </div>
                <p className="text-xs text-zinc-550 leading-relaxed">Standard output contract structure allowing frontend mapping without refactoring web interfaces.</p>
              </div>
            </div>
          </div>
        )}

        {/* Audit Log / History Log Table */}
        <div className="bg-zinc-900/10 border border-zinc-850 rounded-2xl p-6 space-y-6">
          <div className="flex items-center gap-2 border-b border-zinc-900 pb-4">
            <History className="w-5 h-5 text-zinc-400" />
            <h3 className="text-lg font-bold text-white">MongoDB Scan Audit History</h3>
          </div>

          {history.length > 0 ? (
            <div className="overflow-x-auto">
              <table className="w-full text-left border-collapse text-sm text-zinc-400">
                <thead>
                  <tr className="border-b border-zinc-900 text-zinc-500 text-xs font-semibold uppercase tracking-wider">
                    <th className="pb-3 pr-4">File Name</th>
                    <th className="pb-3 px-4">Threat Score</th>
                    <th className="pb-3 px-4">Status</th>
                    <th className="pb-3 px-4">Scan Date</th>
                    <th className="pb-3 pl-4 text-right">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-zinc-900/50">
                  {history.map((item) => {
                    const isAlert = item.status === 'Tampered';
                    const isSuspicious = item.status === 'Suspicious';
                    let badgeColor = 'bg-emerald-500/10 text-emerald-400 border-emerald-500/10';
                    if (isAlert) badgeColor = 'bg-rose-500/10 text-rose-400 border-rose-500/10';
                    if (isSuspicious) badgeColor = 'bg-amber-500/10 text-amber-400 border-amber-500/10';

                    return (
                      <tr key={item._id} className="group hover:bg-zinc-900/20 transition-colors">
                        <td className="py-3.5 pr-4 max-w-[200px] sm:max-w-xs truncate">
                          <button 
                            onClick={() => viewHistoricalScan(item)}
                            className="text-left font-medium text-white hover:text-indigo-400 transition-colors truncate w-full cursor-pointer"
                          >
                            {item.originalName}
                          </button>
                        </td>
                        <td className="py-3.5 px-4 font-mono font-semibold">{item.threatScore}%</td>
                        <td className="py-3.5 px-4">
                          <span className={`px-2 py-0.5 rounded-full text-xs border ${badgeColor}`}>
                            {item.status}
                          </span>
                        </td>
                        <td className="py-3.5 px-4 text-xs text-zinc-550">
                          {new Date(item.createdAt).toLocaleDateString()} &middot; {new Date(item.createdAt).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}
                        </td>
                        <td className="py-3.5 pl-4 text-right">
                          <div className="flex justify-end gap-3 opacity-60 group-hover:opacity-100 transition-opacity">
                            <button 
                              onClick={() => viewHistoricalScan(item)}
                              className="text-xs text-indigo-400 hover:text-indigo-300 font-semibold transition-colors cursor-pointer"
                            >
                              Load
                            </button>
                            <button 
                              onClick={() => handleDeleteScan(item._id)}
                              className="text-zinc-500 hover:text-rose-400 transition-colors cursor-pointer"
                              title="Delete Scan Record"
                            >
                              <Trash2 className="w-4 h-4" />
                            </button>
                          </div>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          ) : (
            <div className="py-10 text-center text-zinc-650 text-xs">
              No historical scan audits registered in MongoDB. Upload files to generate log histories.
            </div>
          )}
        </div>

      </main>

      <Footer />
    </div>
  );
};

export default Dashboard;
