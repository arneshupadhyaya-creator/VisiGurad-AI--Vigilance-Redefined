import React from 'react';
import { Link } from 'react-router-dom';
import { ShieldAlert, Play, Terminal, ArrowRight } from 'lucide-react';

/**
 * Hero Component
 * Displays a premium Stripe-like split layout with high-impact copywriting,
 * glowing background grids, micro-animations, and an interactive developer code mockup.
 */
const Hero = () => {
  return (
    <div className="relative pt-32 pb-20 md:pt-40 md:pb-28 overflow-hidden bg-zinc-950">
      
      {/* Background Glowing Effects */}
      <div className="absolute top-0 left-1/4 w-96 h-96 bg-indigo-500/10 rounded-full blur-[100px] pointer-events-none"></div>
      <div className="absolute bottom-10 right-1/4 w-80 h-80 bg-purple-500/10 rounded-full blur-[120px] pointer-events-none"></div>
      <div className="absolute top-0 left-0 w-full h-full bg-[linear-gradient(to_right,#8080800a_1px,transparent_1px),linear-gradient(to_bottom,#8080800a_1px,transparent_1px)] bg-[size:14px_24px] [mask-image:radial-gradient(ellipse_60%_50%_at_50%_0%,#000_70%,transparent_100%)] pointer-events-none"></div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-12 lg:gap-8 items-center">
          
          {/* Left Block: Heading & Pitch */}
          <div className="lg:col-span-7 text-left space-y-6">
            
            {/* Tagline Badge */}
            <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-zinc-900 border border-zinc-800 text-xs font-medium text-zinc-300">
              <span className="flex h-2 w-2 rounded-full bg-indigo-500 animate-pulse"></span>
              Error Level Analysis (ELA) Core v1.0
            </div>

            {/* Title */}
            <h1 className="text-4xl sm:text-5xl md:text-6xl font-extrabold tracking-tight leading-[1.1] text-white">
              Vigilance Redefined.<br />
              <span className="bg-clip-text text-transparent bg-gradient-to-r from-indigo-400 via-purple-400 to-pink-500">
                Image Tampering Excluded.
              </span>
            </h1>

            {/* Description */}
            <p className="text-base sm:text-lg text-zinc-400 max-w-xl leading-relaxed">
              VisiGuard AI utilizes advanced digital image forensics and Error Level Analysis (ELA) to detect edits, splices, and digital anomalies. Secure your KYC processes, documents, and media assets in milliseconds.
            </p>

            {/* CTA Group */}
            <div className="flex flex-col sm:flex-row gap-4 pt-2">
              <Link 
                to="/dashboard" 
                className="flex items-center justify-center gap-2 px-6 py-3.5 rounded-xl bg-indigo-600 hover:bg-indigo-700 text-white font-semibold text-sm shadow-[0_0_20px_rgba(79,70,229,0.3)] hover:shadow-[0_0_25px_rgba(79,70,229,0.5)] transition-all duration-300 active:scale-95"
              >
                <Play className="w-4 h-4 fill-white" />
                Analyze Image
              </Link>
              <Link 
                to="/docs" 
                className="flex items-center justify-center gap-1.5 px-6 py-3.5 rounded-xl bg-zinc-900 hover:bg-zinc-800 border border-zinc-800 text-zinc-300 hover:text-white font-semibold text-sm transition-all"
              >
                Read API Docs
                <ArrowRight className="w-4 h-4 text-zinc-500 group-hover:translate-x-0.5 transition-transform" />
              </Link>
            </div>
            
          </div>

          {/* Right Block: Stripe-style Interactive Mockup */}
          <div className="lg:col-span-5 relative">
            <div className="absolute inset-0 bg-indigo-500/20 rounded-2xl blur-xl pointer-events-none scale-95 opacity-50"></div>
            
            {/* Terminal Window Mockup */}
            <div className="relative bg-zinc-950/80 backdrop-blur-md rounded-2xl border border-zinc-800 shadow-2xl overflow-hidden font-mono text-xs text-zinc-300">
              
              {/* Terminal Title Bar */}
              <div className="flex items-center justify-between px-4 py-3 bg-zinc-900/50 border-b border-zinc-800/80">
                <div className="flex gap-1.5">
                  <span className="w-3 h-3 rounded-full bg-rose-500/80"></span>
                  <span className="w-3 h-3 rounded-full bg-amber-500/80"></span>
                  <span className="w-3 h-3 rounded-full bg-emerald-500/80"></span>
                </div>
                <div className="flex items-center gap-1.5 text-[10px] text-zinc-500 font-semibold">
                  <Terminal className="w-3.5 h-3.5" />
                  bash - api_scan.sh
                </div>
              </div>

              {/* Code/Terminal Content */}
              <div className="p-5 space-y-4 overflow-x-auto text-left leading-relaxed">
                <div>
                  <span className="text-zinc-500">$</span> <span className="text-indigo-400">curl</span> -X POST https://api.visiguard.ai/v1/scan \
                </div>
                <div className="pl-4">
                  -H <span className="text-emerald-400">"Authorization: Bearer vg_live_8f3d..."</span> \
                </div>
                <div className="pl-4">
                  -F <span className="text-emerald-400">"image=@passport_photo.jpg"</span> \
                </div>
                <div className="pl-4">
                  -F <span className="text-emerald-400">"quality=90"</span>
                </div>

                <div className="pt-2 border-t border-zinc-800/80 text-[10px] text-zinc-500">
                  # Response 201 Created
                </div>

                <div className="text-zinc-400 space-y-1">
                  <div>&#123;</div>
                  <div className="pl-4">"status": <span className="text-emerald-400">"Suspicious"</span>,</div>
                  <div className="pl-4">"threatScore": <span className="text-amber-400">32.4</span>,</div>
                  <div className="pl-4">"elaHighlightUrl": <span className="text-purple-400">"https://cdn.visiguard.ai/ela_310.png"</span>,</div>
                  <div className="pl-4">"metadata": &#123;</div>
                  <div className="pl-8">"width": 1280, "height": 720,</div>
                  <div className="pl-8">"format": "JPEG"</div>
                  <div className="pl-4">&#125;,</div>
                  <div className="pl-4">"anomalies": ["High compression delta near coordinates [420, 150]"]</div>
                  <div>&#125;</div>
                </div>

              </div>

            </div>
          </div>

        </div>
      </div>
    </div>
  );
};

export default Hero;