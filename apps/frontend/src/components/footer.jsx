import React from 'react';
import { Shield } from 'lucide-react';

/**
 * Footer Component
 * Premium multi-column footer matching the Stripe developer-centric aesthetic.
 */
const Footer = () => {
  return (
    <footer className="bg-zinc-950 border-t border-zinc-900 text-zinc-400 py-12 md:py-16 mt-auto">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid grid-cols-2 md:grid-cols-5 gap-8 md:gap-12">
          
          {/* Logo & Description */}
          <div className="col-span-2 space-y-4">
            <div className="flex items-center gap-2">
              <Shield className="w-5 h-5 text-indigo-500" />
              <span className="text-white font-bold text-lg">VisiGuard AI</span>
            </div>
            <p className="text-sm text-zinc-500 max-w-xs leading-relaxed">
              Redefining digital vigilance. Exposing document tampering and image manipulations with cutting-edge analytical tools.
            </p>
          </div>

          {/* Product links */}
          <div>
            <h4 className="text-white text-xs font-semibold uppercase tracking-wider mb-4">Product</h4>
            <ul className="space-y-2.5 text-sm">
              <li><a href="/dashboard" className="hover:text-white transition-colors">Forensic Dashboard</a></li>
              <li><a href="/docs" className="hover:text-white transition-colors">API Sandboxing</a></li>
              <li><span className="text-zinc-600 cursor-not-allowed">Enterprise CLI</span></li>
              <li><span className="text-zinc-600 cursor-not-allowed">Pricing Plans</span></li>
            </ul>
          </div>

          {/* Developer links */}
          <div>
            <h4 className="text-white text-xs font-semibold uppercase tracking-wider mb-4">Developers</h4>
            <ul className="space-y-2.5 text-sm">
              <li><a href="/docs" className="hover:text-white transition-colors">REST API Docs</a></li>
              <li><a href="/docs" className="hover:text-white transition-colors">SDK Integration</a></li>
              <li><a href="https://github.com/arneshupadhyaya-creator/VisiGurad-AI--Vigilance-Redefined" target="_blank" rel="noreferrer" className="hover:text-white transition-colors">GitHub Source</a></li>
              <li><span className="text-zinc-600 cursor-not-allowed">Webhooks</span></li>
            </ul>
          </div>

          {/* Company links */}
          <div>
            <h4 className="text-white text-xs font-semibold uppercase tracking-wider mb-4">Security</h4>
            <ul className="space-y-2.5 text-sm">
              <li><span className="text-zinc-600 cursor-not-allowed">Compliance</span></li>
              <li><span className="text-zinc-600 cursor-not-allowed">Privacy Policy</span></li>
              <li><span className="text-zinc-600 cursor-not-allowed">MongoDB Storage</span></li>
              <li><span className="text-zinc-600 cursor-not-allowed">System Status</span></li>
            </ul>
          </div>

        </div>

        {/* Bottom copyright block */}
        <div className="border-t border-zinc-900/60 mt-12 pt-8 flex flex-col md:flex-row justify-between items-center gap-4 text-xs text-zinc-600">
          <div>
            &copy; {new Date().getFullYear()} VisiGuard AI. All rights reserved. Created in branch Sanskar.
          </div>
          <div className="flex gap-4">
            <span>Redefining Vigilance</span>
            <span>&middot;</span>
            <span>Secure Forensics</span>
          </div>
        </div>

      </div>
    </footer>
  );
};

export default Footer;