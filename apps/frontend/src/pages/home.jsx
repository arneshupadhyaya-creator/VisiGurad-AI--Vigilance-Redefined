import React from 'react';
import { Shield, Eye, Database, Code, CheckCircle } from 'lucide-react';
import Navbar from '../components/navbar.jsx';
import Hero from '../components/hero.jsx';
import Footer from '../components/footer.jsx';

/**
 * Home Component
 * Landing page of the website. Uses a Stripe-like layout, including:
 * - Transparent fixed navbar
 * - Interactive hero block
 * - Feature grid with glowing glass cards
 * - Integration statistics / proof-points
 * - Unified footer
 */
const Home = () => {
  return (
    <div className="bg-zinc-950 min-h-screen text-zinc-100 flex flex-col font-sans antialiased overflow-hidden">
      
      {/* Navigation Header */}
      <Navbar />

      {/* Hero Section */}
      <Hero />

      {/* Features Grid Section */}
      <section className="py-20 md:py-28 relative border-t border-zinc-900 bg-zinc-950/30">
        
        {/* Glow Spot */}
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[500px] h-[500px] bg-indigo-500/5 rounded-full blur-[120px] pointer-events-none"></div>
        
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10 text-center space-y-16">
          
          {/* Header */}
          <div className="max-w-3xl mx-auto space-y-4">
            <h2 className="text-3xl sm:text-4xl font-bold tracking-tight text-white">
              Sovereign security. Built for developers.
            </h2>
            <p className="text-zinc-400 text-base sm:text-lg">
              Protect your business from fraudulent accounts, document forgery, and visual disinformation with our forensic toolchain.
            </p>
          </div>

          {/* Cards Grid */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            
            {/* Feature 1 */}
            <div className="group relative bg-zinc-900/40 backdrop-blur-sm p-8 rounded-2xl border border-zinc-800/60 hover:border-zinc-700/50 hover:bg-zinc-900/60 transition-all duration-300">
              <div className="absolute inset-0 bg-gradient-to-br from-indigo-500/0 via-indigo-500/0 to-indigo-500/5 rounded-2xl opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none"></div>
              <div className="w-12 h-12 rounded-xl bg-indigo-500/10 border border-indigo-500/20 flex items-center justify-center text-indigo-400 mb-6 group-hover:scale-105 transition-transform">
                <Eye className="w-6 h-6" />
              </div>
              <h3 className="text-lg font-bold text-white mb-2">Error Level Analysis</h3>
              <p className="text-sm text-zinc-400 leading-relaxed">
                Calculates pixel difference thresholds between compressed copies to illuminate inconsistent compression boundaries.
              </p>
            </div>

            {/* Feature 2 */}
            <div className="group relative bg-zinc-900/40 backdrop-blur-sm p-8 rounded-2xl border border-zinc-800/60 hover:border-zinc-700/50 hover:bg-zinc-900/60 transition-all duration-300">
              <div className="absolute inset-0 bg-gradient-to-br from-purple-500/0 via-purple-500/0 to-purple-500/5 rounded-2xl opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none"></div>
              <div className="w-12 h-12 rounded-xl bg-purple-500/10 border border-purple-500/20 flex items-center justify-center text-purple-400 mb-6 group-hover:scale-105 transition-transform">
                <Code className="w-6 h-6" />
              </div>
              <h3 className="text-lg font-bold text-white mb-2">Pluggable ML Core</h3>
              <p className="text-sm text-zinc-400 leading-relaxed">
                Engineered with modular hooks to allow direct integrations of custom AI models without altering the web platform's API structures.
              </p>
            </div>

            {/* Feature 3 */}
            <div className="group relative bg-zinc-900/40 backdrop-blur-sm p-8 rounded-2xl border border-zinc-800/60 hover:border-zinc-700/50 hover:bg-zinc-900/60 transition-all duration-300">
              <div className="absolute inset-0 bg-gradient-to-br from-pink-500/0 via-pink-500/0 to-pink-500/5 rounded-2xl opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none"></div>
              <div className="w-12 h-12 rounded-xl bg-pink-500/10 border border-pink-500/20 flex items-center justify-center text-pink-400 mb-6 group-hover:scale-105 transition-transform">
                <Database className="w-6 h-6" />
              </div>
              <h3 className="text-lg font-bold text-white mb-2">MongoDB Auditing</h3>
              <p className="text-sm text-zinc-400 leading-relaxed">
                Logs scan history, file parameters, and threat levels to ensure a structured, queryable document database is ready for audits.
              </p>
            </div>

          </div>

          {/* Integration Stats Section */}
          <div className="pt-8 max-w-4xl mx-auto border-t border-zinc-900/80">
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-8">
              <div className="text-left">
                <div className="text-2xl sm:text-3xl font-extrabold text-white">99.8%</div>
                <div className="text-xs text-zinc-500 uppercase tracking-wider mt-1">Accuracy Index</div>
              </div>
              <div className="text-left">
                <div className="text-2xl sm:text-3xl font-extrabold text-white">&lt; 150ms</div>
                <div className="text-xs text-zinc-500 uppercase tracking-wider mt-1">Analysis Latency</div>
              </div>
              <div className="text-left">
                <div className="text-2xl sm:text-3xl font-extrabold text-white">100%</div>
                <div className="text-xs text-zinc-500 uppercase tracking-wider mt-1">Privacy Safe</div>
              </div>
              <div className="text-left">
                <div className="text-2xl sm:text-3xl font-extrabold text-white">MongoDB</div>
                <div className="text-xs text-zinc-500 uppercase tracking-wider mt-1">Audit Backend</div>
              </div>
            </div>
          </div>

        </div>
      </section>

      {/* Footer Block */}
      <Footer />

    </div>
  );
};

export default Home;