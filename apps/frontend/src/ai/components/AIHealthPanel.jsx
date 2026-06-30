import React, { useState, useEffect } from 'react';
import { getAIStatus } from '../services/aiClient';
import { Activity, RefreshCw, Cpu, Server, Database, HardDrive, Loader2 } from 'lucide-react';

/**
 * AIHealthPanel Component
 * Purpose: Visualizes cybersecurity local AI inference node health, model loadings, and queue metrics.
 * Responsibility: Fetch telemetry metrics from `/ai/status` and render in a glassmorphic system diagnostic layout.
 */
export const AIHealthPanel = () => {
  const [metrics, setMetrics] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const fetchMetrics = async () => {
    setLoading(true);
    setError('');
    try {
      const response = await getAIStatus();
      if (response.status === 'success') {
        setMetrics(response.data);
      }
    } catch (err) {
      setError(err.response?.data?.error || err.message || 'AI Node Offline');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchMetrics();
    // Poll metrics every 15 seconds
    const interval = setInterval(fetchMetrics, 15000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="space-y-6 text-left">
      <div className="flex items-center justify-between border-b border-zinc-900 pb-4">
        <div className="flex items-center gap-2">
          <Activity className="w-5 h-5 text-indigo-400" />
          <div>
            <h3 className="text-lg font-bold text-white">Local AI Coprocessor Diagnostics</h3>
            <p className="text-zinc-500 text-xs mt-0.5">Real-time health indices of dedicated on-premise inference engines.</p>
          </div>
        </div>
        <button
          onClick={fetchMetrics}
          disabled={loading}
          className="p-2 bg-zinc-900 border border-zinc-800 hover:border-zinc-700 text-zinc-400 hover:text-white rounded-lg transition-colors cursor-pointer disabled:opacity-50"
        >
          {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <RefreshCw className="w-4 h-4" />}
        </button>
      </div>

      {error && (
        <div className="p-4 bg-rose-500/5 border border-rose-500/20 text-rose-400 rounded-xl text-xs flex items-center gap-2">
          <Server className="w-4.5 h-4.5 animate-pulse" />
          <span><strong>Diagnostics Error:</strong> {error}. Local inference simulation drivers are serving requests.</span>
        </div>
      )}

      {metrics && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {/* Card 1: Node status */}
          <div className="bg-zinc-900/30 border border-zinc-800 rounded-2xl p-5 space-y-3 relative overflow-hidden group hover:border-zinc-700/50 transition-colors">
            <div className="flex justify-between items-start">
              <span className="text-[10px] font-bold text-zinc-500 uppercase tracking-widest">Inference Node</span>
              <Cpu className="w-4.5 h-4.5 text-indigo-400" />
            </div>
            <div className="space-y-1">
              <span className="text-xl font-extrabold text-white flex items-center gap-1.5">
                {metrics.aiAvailable ? (
                  <>
                    <div className="w-2 h-2 rounded-full bg-emerald-500 animate-ping"></div>
                    Online
                  </>
                ) : (
                  'Offline'
                )}
              </span>
              <p className="text-[11px] text-zinc-500 truncate">{metrics.modelLoaded}</p>
            </div>
          </div>

          {/* Card 2: Average response time */}
          <div className="bg-zinc-900/30 border border-zinc-800 rounded-2xl p-5 space-y-3 relative overflow-hidden group hover:border-zinc-700/50 transition-colors">
            <div className="flex justify-between items-start">
              <span className="text-[10px] font-bold text-zinc-500 uppercase tracking-widest">Inference Latency</span>
              <Server className="w-4.5 h-4.5 text-indigo-400" />
            </div>
            <div className="space-y-1">
              <span className="text-xl font-extrabold text-white">
                {metrics.averageResponseTime} ms
              </span>
              <p className="text-[11px] text-zinc-500">Average response computation duration</p>
            </div>
          </div>

          {/* Card 3: Memory usage */}
          <div className="bg-zinc-900/30 border border-zinc-800 rounded-2xl p-5 space-y-3 relative overflow-hidden group hover:border-zinc-700/50 transition-colors">
            <div className="flex justify-between items-start">
              <span className="text-[10px] font-bold text-zinc-500 uppercase tracking-widest">Coprocessor VRAM</span>
              <HardDrive className="w-4.5 h-4.5 text-indigo-400" />
            </div>
            <div className="space-y-1">
              <span className="text-xl font-extrabold text-white">
                {metrics.memoryUsage.percentage}%
              </span>
              <p className="text-[11px] text-zinc-500">{metrics.memoryUsage.usedMB} / {metrics.memoryUsage.totalMB} MB allocated</p>
            </div>
          </div>

          {/* Card 4: Queue size */}
          <div className="bg-zinc-900/30 border border-zinc-800 rounded-2xl p-5 space-y-3 relative overflow-hidden group hover:border-zinc-700/50 transition-colors">
            <div className="flex justify-between items-start">
              <span className="text-[10px] font-bold text-zinc-500 uppercase tracking-widest">Inference Queue</span>
              <Database className="w-4.5 h-4.5 text-indigo-400" />
            </div>
            <div className="space-y-1">
              <span className="text-xl font-extrabold text-white">
                {metrics.queueSize}
              </span>
              <p className="text-[11px] text-zinc-500">Total requests currently queued: {metrics.totalProcessed} processed</p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
