import React, { useState } from 'react';
import { Terminal, Shield, BookOpen, Code, Layers, Database, ChevronRight, Copy, Check } from 'lucide-react';
import Navbar from '../components/navbar.jsx';
import Footer from '../components/footer.jsx';

/**
 * Docs Component
 * Stripe-like API documentation page. Shows a 3-column developer layout:
 * - Left: Navigation links to guides
 * - Center: API description, explanations, and parameter tables
 * - Right: Interactive code blocks with copy-to-clipboard for curl, Node.js, and Python.
 */
const Docs = () => {
  const [activeTab, setActiveTab] = useState('curl');
  const [copied, setCopied] = useState(false);
  const [activeSection, setActiveSection] = useState('getting-started');

  const codeSnippets = {
    curl: `curl -X POST http://localhost:5000/api/scan \\
  -H "Content-Type: multipart/form-data" \\
  -F "image=@/path/to/identity_doc.jpg"`,
    
    node: `const axios = require('axios');
const FormData = require('form-data');
const fs = require('fs');

const form = new FormData();
form.append('image', fs.createReadStream('/path/to/identity_doc.jpg'));

axios.post('http://localhost:5000/api/scan', form, {
  headers: form.getHeaders()
})
.then(response => {
  console.log('Tamper Score:', response.data.scan.threatScore);
  console.log('Audit Status:', response.data.scan.status);
})
.catch(error => {
  console.error('Forensic Scan Error:', error.message);
});`,
    
    python: `import requests

url = "http://localhost:5000/api/scan"
files = {
    "image": ("identity_doc.jpg", open("/path/to/identity_doc.jpg", "rb"), "image/jpeg")
}

response = requests.post(url, files=files)
data = response.json()

print(f"Tamper Score: {data['scan']['threatScore']}%")
print(f"Audit Status: {data['scan']['status']}")`
  };

  const handleCopy = () => {
    navigator.clipboard.writeText(codeSnippets[activeTab]);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const menuSections = [
    { id: 'getting-started', label: 'Getting Started', icon: BookOpen },
    { id: 'scan-endpoint', label: 'Scan API Endpoint', icon: Code },
    { id: 'custom-ml', label: 'Self-Made AI Models', icon: Layers },
    { id: 'db-schema', label: 'MongoDB Schema', icon: Database },
  ];

  return (
    <div className="bg-zinc-950 min-h-screen text-zinc-100 flex flex-col font-sans">
      <Navbar />

      {/* Main Container */}
      <div className="flex-grow max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-28 pb-16 w-full flex flex-col lg:flex-row gap-8 items-start">
        
        {/* Left Column: Docs Navigation (Sticky on desktop) */}
        <aside className="w-full lg:w-64 flex-shrink-0 lg:sticky lg:top-28 space-y-1 bg-zinc-950/20 p-4 rounded-2xl border border-zinc-900 lg:border-transparent">
          <div className="text-xs font-bold text-zinc-500 uppercase tracking-wider px-3 mb-3">API Guide</div>
          {menuSections.map((sect) => {
            const Icon = sect.icon;
            const isSel = activeSection === sect.id;
            return (
              <button
                key={sect.id}
                onClick={() => {
                  setActiveSection(sect.id);
                  document.getElementById(sect.id)?.scrollIntoView({ behavior: 'smooth', block: 'start' });
                }}
                className={`w-full flex items-center justify-between px-3 py-2.5 rounded-lg text-sm transition-all text-left ${
                  isSel 
                    ? 'bg-indigo-500/10 text-white font-semibold border-l-2 border-indigo-500 pl-2.5' 
                    : 'text-zinc-400 hover:text-white hover:bg-zinc-900/50'
                }`}
              >
                <div className="flex items-center gap-2.5">
                  <Icon className={`w-4 h-4 ${isSel ? 'text-indigo-400' : 'text-zinc-500'}`} />
                  {sect.label}
                </div>
                <ChevronRight className={`w-3.5 h-3.5 text-zinc-600 transition-transform ${isSel ? 'translate-x-0.5' : ''}`} />
              </button>
            );
          })}
        </aside>

        {/* Middle Column: Detailed Documentation Guides */}
        <main className="flex-grow w-full lg:max-w-xl text-left space-y-16">
          
          {/* Getting Started Guide */}
          <section id="getting-started" className="space-y-4 scroll-mt-28">
            <h2 className="text-2xl font-bold text-white flex items-center gap-2">
              <BookOpen className="w-5 h-5 text-indigo-500" />
              Getting Started
            </h2>
            <p className="text-zinc-400 text-sm leading-relaxed">
              VisiGuard AI operates a MERN Stack architecture configured for developer integration. By running standard HTTP multipart POST endpoints, you can trigger visual forensics analyses programmatically from server configurations, web applications, or custom pipelines.
            </p>
            <div className="p-4 bg-zinc-900/40 rounded-xl border border-zinc-800/80 text-xs text-zinc-400 space-y-2">
              <strong className="text-white text-xs block">Default Service Environment</strong>
              <div className="flex justify-between font-mono">
                <span>Frontend Server:</span>
                <span className="text-zinc-300">http://localhost:5173</span>
              </div>
              <div className="flex justify-between font-mono">
                <span>Backend API Server:</span>
                <span className="text-indigo-400">http://localhost:5000</span>
              </div>
            </div>
          </section>

          {/* Scan API Endpoint */}
          <section id="scan-endpoint" className="space-y-4 scroll-mt-28">
            <h2 className="text-2xl font-bold text-white flex items-center gap-2">
              <Code className="w-5 h-5 text-indigo-500" />
              Analyze Digital Assets (`POST /api/scan`)
            </h2>
            <p className="text-zinc-400 text-sm leading-relaxed">
              Accepts a multipart file upload of an image, performs Error Level Analysis (ELA) compression scans, calculates threat indices, saves records to MongoDB, and returns audit metrics.
            </p>

            {/* Parameters Table */}
            <div className="border border-zinc-900 rounded-xl overflow-hidden text-xs">
              <table className="w-full text-left border-collapse">
                <thead>
                  <tr className="bg-zinc-900/50 text-zinc-400 font-bold border-b border-zinc-900">
                    <th className="p-3">Field</th>
                    <th className="p-3">Type</th>
                    <th className="p-3">Required</th>
                    <th className="p-3">Description</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-zinc-900 text-zinc-400">
                  <tr>
                    <td className="p-3 font-semibold text-white font-mono">image</td>
                    <td className="p-3 text-zinc-500">File</td>
                    <td className="p-3 text-indigo-400">Yes</td>
                    <td className="p-3">JPEG, JPG, or PNG image file (&lt;10MB).</td>
                  </tr>
                  <tr>
                    <td className="p-3 font-semibold text-white font-mono">quality</td>
                    <td className="p-3 text-zinc-500">Integer</td>
                    <td className="p-3 text-zinc-600">No</td>
                    <td className="p-3">Target compression resave ratio. Defaults to `90`.</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </section>

          {/* Custom ML Hook Explanation */}
          <section id="custom-ml" className="space-y-4 scroll-mt-28">
            <h2 className="text-2xl font-bold text-white flex items-center gap-2">
              <Layers className="w-5 h-5 text-indigo-500" />
              Integrating Self-Made AI Models
            </h2>
            <p className="text-zinc-400 text-sm leading-relaxed">
              VisiGuard AI supports plugging in custom machine learning scripts. The backend architecture decouples visual processing from the main HTTP loop. 
            </p>
            <div className="bg-zinc-900/30 border border-zinc-850 p-5 rounded-2xl space-y-3 text-xs leading-relaxed text-zinc-400">
              <div className="flex items-center gap-2 text-white font-semibold mb-1">
                <Shield className="w-4 h-4 text-indigo-400" />
                How the custom AI pipeline works:
              </div>
              <ol className="list-decimal list-inside space-y-2.5">
                <li>
                  When an image is posted, the backend writes the file to the <code className="text-zinc-300 font-mono text-[10px]">Backend/uploads/</code> directory.
                </li>
                <li>
                  The backend calls a subprocess executing the <code className="text-zinc-300 font-mono text-[10px]">ML/cli.py</code> wrapper script.
                </li>
                <li>
                  The script executes the <code className="text-zinc-300 font-mono text-[10px]">generate_ela()</code> logic and returns a structured JSON payload to stdout.
                </li>
                <li>
                  To hook in a custom PyTorch/TensorFlow classification or object detection model, developers can modify the python outputs in <code className="text-indigo-400 font-mono text-[10px]">ML/cli.py</code>.
                </li>
              </ol>
            </div>
          </section>

          {/* Database Schema */}
          <section id="db-schema" className="space-y-4 scroll-mt-28">
            <h2 className="text-2xl font-bold text-white flex items-center gap-2">
              <Database className="w-5 h-5 text-indigo-500" />
              MongoDB Database Structure
            </h2>
            <p className="text-zinc-400 text-sm leading-relaxed">
              Audit data is stored in the MongoDB database under the `Scans` collection. Fields mapped by the Mongoose connector are:
            </p>
            <div className="bg-zinc-900/20 border border-zinc-900 rounded-xl p-4 font-mono text-[11px] text-zinc-400 space-y-1.5 leading-relaxed">
              <div><span className="text-indigo-400">originalName</span>: String <span className="text-zinc-600">// E.g. "my_passport.jpg"</span></div>
              <div><span className="text-indigo-400">originalPath</span>: String <span className="text-zinc-600">// Web path to access source file</span></div>
              <div><span className="text-indigo-400">elaPath</span>: String <span className="text-zinc-600">// Web path to error level highlights</span></div>
              <div><span className="text-indigo-400">fileSize</span>: Number <span className="text-zinc-600">// In bytes</span></div>
              <div><span className="text-indigo-400">threatScore</span>: Number <span className="text-zinc-600">// Evaluated anomaly score (0.0 to 100.0)</span></div>
              <div><span className="text-indigo-400">status</span>: String <span className="text-zinc-600">// 'Clean', 'Suspicious', or 'Tampered'</span></div>
              <div><span className="text-indigo-400">createdAt</span>: Date <span className="text-zinc-600">// Audit timestamp</span></div>
            </div>
          </section>

        </main>

        {/* Right Column: Code Playground / Code Snippets (Sticky on desktop) */}
        <div className="w-full lg:w-96 flex-shrink-0 lg:sticky lg:top-28 space-y-3">
          <div className="bg-zinc-900/60 border border-zinc-800 rounded-2xl overflow-hidden shadow-2xl">
            
            {/* Window Title / Tabs */}
            <div className="flex items-center justify-between px-4 py-3 bg-zinc-900 border-b border-zinc-800/80">
              <div className="flex gap-2">
                <button 
                  onClick={() => setActiveTab('curl')}
                  className={`text-[10px] font-bold uppercase tracking-wider pb-1 px-1.5 border-b-2 transition-all ${
                    activeTab === 'curl' ? 'text-indigo-400 border-indigo-500' : 'text-zinc-500 border-transparent hover:text-zinc-300'
                  }`}
                >
                  cURL
                </button>
                <button 
                  onClick={() => setActiveTab('node')}
                  className={`text-[10px] font-bold uppercase tracking-wider pb-1 px-1.5 border-b-2 transition-all ${
                    activeTab === 'node' ? 'text-indigo-400 border-indigo-500' : 'text-zinc-500 border-transparent hover:text-zinc-300'
                  }`}
                >
                  Node.js
                </button>
                <button 
                  onClick={() => setActiveTab('python')}
                  className={`text-[10px] font-bold uppercase tracking-wider pb-1 px-1.5 border-b-2 transition-all ${
                    activeTab === 'python' ? 'text-indigo-400 border-indigo-500' : 'text-zinc-500 border-transparent hover:text-zinc-300'
                  }`}
                >
                  Python
                </button>
              </div>

              {/* Copy Code */}
              <button 
                onClick={handleCopy}
                className="text-zinc-500 hover:text-zinc-300 transition-colors p-1 rounded-md bg-zinc-950 border border-zinc-850 flex items-center gap-1 text-[10px] font-semibold"
                title="Copy code to clipboard"
              >
                {copied ? <Check className="w-3 h-3 text-emerald-400" /> : <Copy className="w-3 h-3" />}
                {copied ? 'Copied' : 'Copy'}
              </button>
            </div>

            {/* Code Body */}
            <div className="p-4 bg-zinc-950 font-mono text-[10px] text-zinc-300 overflow-x-auto text-left leading-relaxed max-h-[350px]">
              <pre className="whitespace-pre">
                {codeSnippets[activeTab]}
              </pre>
            </div>

          </div>
          
          <div className="text-[10px] text-zinc-500 text-center flex items-center justify-center gap-1.5">
            <Terminal className="w-3 h-3" />
            Runs in sandbox environment
          </div>
        </div>

      </div>

      <Footer />
    </div>
  );
};

export default Docs;
