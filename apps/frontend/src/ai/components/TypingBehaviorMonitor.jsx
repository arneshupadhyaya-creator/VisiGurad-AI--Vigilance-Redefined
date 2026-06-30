import React, { useState } from 'react';
import { AlertTriangle, ShieldCheck, ShieldAlert, CheckCircle } from 'lucide-react';

/**
 * TypingBehaviorMonitor Component
 * Purpose: Render graduated alerts and verification barriers based on computed keystroke threat risk.
 * Responsibility: Capture user verification clicks to bypass Bot Lock indicators.
 */
export const TypingBehaviorMonitor = ({ riskLevel, onResolveVerification }) => {
  const [verified, setVerified] = useState(false);

  const handleVerify = () => {
    setVerified(true);
    if (onResolveVerification) {
      onResolveVerification();
    }
  };

  if (riskLevel === 'LOW') {
    return null;
  }

  return (
    <div className="space-y-4 text-left transition-all duration-300">
      {/* MEDIUM RISK ALERT */}
      {riskLevel === 'MEDIUM' && (
        <div className="p-3.5 bg-amber-500/5 border border-amber-500/20 text-amber-400 rounded-xl text-xs flex items-start gap-2.5">
          <AlertTriangle className="w-4.5 h-4.5 flex-shrink-0 mt-0.5" />
          <div>
            <span className="font-semibold block text-white mb-0.5">Subtle Input Deviation</span>
            <p className="text-zinc-400 leading-relaxed">Flight time consistency parameters deviate slightly from average patterns. Input source is monitored.</p>
          </div>
        </div>
      )}

      {/* HIGH RISK ALERT */}
      {riskLevel === 'HIGH' && (
        <div className="p-4 bg-rose-500/5 border border-rose-500/25 text-rose-400 rounded-xl text-xs flex items-start gap-3">
          <ShieldAlert className="w-5 h-5 flex-shrink-0 mt-0.5 animate-pulse" />
          <div>
            <span className="font-bold block text-white mb-0.5">High Severity Alert: Robot input profile</span>
            <p className="text-zinc-400 leading-relaxed">Typing speed consistent variance indicates possible macro or scripted input sequence. Verification flags recorded in audit ledger.</p>
          </div>
        </div>
      )}

      {/* VERY HIGH RISK LOCKOUT BLOCK */}
      {riskLevel === 'VERY_HIGH' && (
        <div className="p-5 bg-rose-950/20 border border-rose-500/40 rounded-2xl space-y-4">
          <div className="flex items-start gap-3.5">
            <ShieldAlert className="w-6 h-6 text-rose-500 flex-shrink-0 mt-0.5 animate-bounce" />
            <div className="space-y-1">
              <h4 className="text-sm font-bold text-white">System Security Interlock: Verification Required</h4>
              <p className="text-xs text-zinc-400 leading-relaxed">
                Autonomous inputs detected (e.g. pasting large credential blocks or robotic consistency metrics). Your console session is temporarily halted.
              </p>
            </div>
          </div>

          {verified ? (
            <div className="p-3 bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 rounded-xl text-xs flex items-center gap-2">
              <CheckCircle className="w-4 h-4" />
              <span>Identity Verified. Safe access resumed.</span>
            </div>
          ) : (
            <div className="pt-2">
              <button
                onClick={handleVerify}
                className="px-5 py-2.5 bg-rose-600 hover:bg-rose-700 text-white font-semibold text-xs rounded-xl shadow-md transition-all cursor-pointer hover:shadow-[0_0_15px_rgba(239,68,68,0.2)] active:scale-95"
              >
                Confirm Human Operations
              </button>
            </div>
          )}
        </div>
      )}
    </div>
  );
};
