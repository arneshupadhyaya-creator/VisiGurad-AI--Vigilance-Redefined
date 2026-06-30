import React, { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import { Shield, Eye, EyeOff, Loader2, UserPlus, Check, X, AlertTriangle } from 'lucide-react';
import Navbar from '../components/navbar.jsx';
import Footer from '../components/footer.jsx';

/**
 * Register Page
 * Purpose: Allows new security auditors to sign up.
 * Design: High-contrast layout with live password parameter visual indicators.
 */
const Register = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [errorMsg, setErrorMsg] = useState('');
  const [submitting, setSubmitting] = useState(false);

  // Password Requirement States
  const [checks, setChecks] = useState({
    length: false,
    uppercase: false,
    lowercase: false,
    number: false
  });

  const { register } = useAuth();
  const navigate = useNavigate();

  // Run checks on password input
  useEffect(() => {
    setChecks({
      length: password.length >= 8,
      uppercase: /[A-Z]/.test(password),
      lowercase: /[a-z]/.test(password),
      number: /[0-9]/.test(password)
    });
  }, [password]);

  const allValid = Object.values(checks).every(Boolean);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setErrorMsg('');

    if (!email || !password) {
      setErrorMsg('All fields are required.');
      return;
    }

    if (!allValid) {
      setErrorMsg('Please satisfy all password complexity criteria.');
      return;
    }

    setSubmitting(true);
    try {
      const success = await register(email, password);
      if (success) {
        navigate('/dashboard');
      }
    } catch (err) {
      setErrorMsg(err.message || 'Registration failed. That account might already exist.');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="bg-zinc-950 min-h-screen text-zinc-100 flex flex-col font-sans antialiased overflow-x-hidden">
      <Navbar />

      <div className="flex-grow flex items-center justify-center pt-28 pb-16 px-4 relative">
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[400px] h-[400px] bg-purple-500/5 rounded-full blur-[100px] pointer-events-none"></div>

        <div className="w-full max-w-md relative z-10">
          <div className="bg-zinc-900/40 border border-zinc-800/80 backdrop-blur-md rounded-2xl p-8 shadow-2xl transition-all duration-300 hover:border-zinc-700/50">
            {/* Header */}
            <div className="text-center space-y-2 mb-6">
              <div className="mx-auto w-12 h-12 rounded-xl bg-purple-500/10 border border-purple-500/20 flex items-center justify-center text-purple-400">
                <Shield className="w-6 h-6" />
              </div>
              <h2 className="text-2xl font-bold tracking-tight text-white">Create auditor account</h2>
              <p className="text-zinc-400 text-xs sm:text-sm">Initiate your sovereign digital forensics session</p>
            </div>

            {/* Error alerts */}
            {errorMsg && (
              <div className="mb-4 p-4 bg-rose-500/10 border border-rose-500/25 text-rose-400 rounded-xl text-xs flex items-center gap-2.5">
                <AlertTriangle className="w-4 h-4 flex-shrink-0" />
                <span>{errorMsg}</span>
              </div>
            )}

            {/* Form */}
            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="space-y-1.5 text-left">
                <label className="text-xs font-semibold text-zinc-400 uppercase tracking-wider">Email Address</label>
                <input 
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="name@company.com"
                  className="w-full bg-zinc-950 border border-zinc-800 hover:border-zinc-700 focus:border-purple-500 focus:ring-1 focus:ring-purple-500/50 text-white rounded-xl px-4 py-3 text-sm transition-all outline-none"
                  required
                />
              </div>

              <div className="space-y-1.5 text-left">
                <label className="text-xs font-semibold text-zinc-400 uppercase tracking-wider">Password</label>
                <div className="relative">
                  <input 
                    type={showPassword ? 'text' : 'password'}
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    placeholder="••••••••"
                    className="w-full bg-zinc-950 border border-zinc-800 hover:border-zinc-700 focus:border-purple-500 focus:ring-1 focus:ring-purple-500/50 text-white rounded-xl pl-4 pr-10 py-3 text-sm transition-all outline-none"
                    required
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="absolute right-3 top-1/2 -translate-y-1/2 text-zinc-500 hover:text-white transition-colors"
                  >
                    {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                  </button>
                </div>
              </div>

              {/* Password Visual Checkup Grid */}
              <div className="grid grid-cols-2 gap-2.5 p-3.5 bg-zinc-950 rounded-xl border border-zinc-900 text-left">
                <div className="flex items-center gap-1.5 text-[10px] sm:text-xs">
                  {checks.length ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <X className="w-3.5 h-3.5 text-zinc-600" />}
                  <span className={checks.length ? 'text-zinc-300' : 'text-zinc-650'}>8+ Characters</span>
                </div>
                <div className="flex items-center gap-1.5 text-[10px] sm:text-xs">
                  {checks.uppercase ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <X className="w-3.5 h-3.5 text-zinc-600" />}
                  <span className={checks.uppercase ? 'text-zinc-300' : 'text-zinc-650'}>1 Uppercase</span>
                </div>
                <div className="flex items-center gap-1.5 text-[10px] sm:text-xs">
                  {checks.lowercase ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <X className="w-3.5 h-3.5 text-zinc-600" />}
                  <span className={checks.lowercase ? 'text-zinc-300' : 'text-zinc-650'}>1 Lowercase</span>
                </div>
                <div className="flex items-center gap-1.5 text-[10px] sm:text-xs">
                  {checks.number ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <X className="w-3.5 h-3.5 text-zinc-600" />}
                  <span className={checks.number ? 'text-zinc-300' : 'text-zinc-650'}>1 Number</span>
                </div>
              </div>

              <button
                type="submit"
                disabled={submitting || !allValid}
                className="w-full flex items-center justify-center gap-2 py-3 bg-purple-650 hover:bg-purple-600 active:scale-98 disabled:opacity-40 text-white font-semibold text-sm rounded-xl transition-all shadow-[0_0_20px_rgba(147,51,234,0.15)] mt-2"
              >
                {submitting ? (
                  <>
                    <Loader2 className="w-4 h-4 animate-spin" />
                    Registering details...
                  </>
                ) : (
                  <>
                    Create Account
                    <UserPlus className="w-4 h-4" />
                  </>
                )}
              </button>
            </form>

            <div className="text-center mt-6 pt-6 border-t border-zinc-900 text-xs text-zinc-500">
              Already have an account?{' '}
              <Link to="/login" className="text-purple-400 font-semibold hover:underline">
                Sign in
              </Link>
            </div>

          </div>
        </div>
      </div>

      <Footer />
    </div>
  );
};

export default Register;
