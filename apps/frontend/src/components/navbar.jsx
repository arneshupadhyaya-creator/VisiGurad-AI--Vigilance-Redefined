import React, { useState, useEffect } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import { Shield, Menu, X, ChevronRight, LogOut, LayoutDashboard } from 'lucide-react';

/**
 * Navbar Component
 * Stripe-inspired navigation bar with backdrop blur, glassmorphic layout,
 * and high-contrast, auth-aware glowing action buttons.
 */
const Navbar = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [scrolled, setScrolled] = useState(false);
  const location = useLocation();
  const { isAuthenticated, logout, user } = useAuth();

  // Add scroll listener to make navbar solid on scroll
  useEffect(() => {
    const handleScroll = () => {
      if (window.scrollY > 20) {
        setScrolled(true);
      } else {
        setScrolled(false);
      }
    };
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  // Check if a link is active
  const isActive = (path) => location.pathname === path;

  return (
    <nav className={`fixed top-0 left-0 w-full z-50 transition-all duration-300 ${
      scrolled 
        ? 'bg-zinc-950/85 backdrop-blur-md border-b border-zinc-800/60 shadow-lg' 
        : 'bg-transparent border-b border-transparent'
    }`}>
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-20">
          
          {/* Logo Area */}
          <div className="flex items-center">
            <Link to="/" className="flex items-center gap-2 group">
              <div className="p-2 rounded-lg bg-indigo-500/10 border border-indigo-500/20 group-hover:border-indigo-500/50 transition-all">
                <Shield className="w-6 h-6 text-indigo-400 group-hover:text-indigo-300 transition-colors" />
              </div>
              <span className="text-xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-white via-zinc-200 to-zinc-400">
                VisiGuard <span className="text-indigo-400 font-medium text-lg">AI</span>
              </span>
            </Link>
          </div>

          {/* Desktop Navigation */}
          <div className="hidden md:flex items-center gap-8">
            <Link 
              to="/" 
              className={`text-sm font-medium transition-colors hover:text-white ${
                isActive('/') ? 'text-white font-semibold' : 'text-zinc-400'
              }`}
            >
              Overview
            </Link>
            {isAuthenticated && (
              <Link 
                to="/dashboard" 
                className={`text-sm font-medium transition-colors hover:text-white ${
                  isActive('/dashboard') ? 'text-white font-semibold' : 'text-zinc-400'
                }`}
              >
                Dashboard
              </Link>
            )}
            <Link 
              to="/docs" 
              className={`text-sm font-medium transition-colors hover:text-white ${
                isActive('/docs') ? 'text-white font-semibold' : 'text-zinc-400'
              }`}
            >
              API Docs
            </Link>
          </div>

          {/* Call to Action Button */}
          <div className="hidden md:flex items-center gap-4">
            {isAuthenticated ? (
              <div className="flex items-center gap-4">
                <span className="text-xs text-zinc-400 font-medium">
                  {user?.email}
                </span>
                <Link
                  to="/dashboard"
                  className="flex items-center gap-1.5 text-xs text-indigo-450 hover:text-indigo-400 font-semibold"
                >
                  <LayoutDashboard className="w-4 h-4" />
                  Console
                </Link>
                <button
                  onClick={logout}
                  className="flex items-center gap-1.5 text-xs text-zinc-400 hover:text-rose-450 font-semibold cursor-pointer transition-colors"
                >
                  <LogOut className="w-4 h-4" />
                  Sign Out
                </button>
              </div>
            ) : (
              <div className="flex items-center gap-4">
                <Link 
                  to="/login"
                  className="text-xs font-semibold text-zinc-400 hover:text-white transition-colors"
                >
                  Sign In
                </Link>
                <Link 
                  to="/register" 
                  className="relative group overflow-hidden rounded-full p-[1px] focus:outline-none"
                >
                  <span className="absolute inset-0 bg-gradient-to-r from-indigo-500 via-purple-500 to-pink-500 rounded-full transition-all duration-300 group-hover:scale-105 group-hover:blur-[2px]"></span>
                  <span className="relative flex items-center gap-1.5 px-5 py-2 bg-zinc-950 text-white text-xs font-semibold rounded-full border border-zinc-800 transition-all duration-300 group-hover:bg-zinc-900">
                    Get Started
                    <ChevronRight className="w-4 h-4 text-indigo-400 group-hover:translate-x-0.5 transition-transform" />
                  </span>
                </Link>
              </div>
            )}
          </div>

          {/* Mobile Menu Button */}
          <div className="md:hidden">
            <button
              onClick={() => setIsOpen(!isOpen)}
              className="p-2 rounded-md text-zinc-400 hover:text-white focus:outline-none"
            >
              {isOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
            </button>
          </div>

        </div>
      </div>

      {/* Mobile Drawer */}
      <div className={`md:hidden overflow-hidden transition-all duration-300 ${
        isOpen ? 'max-h-80 border-b border-zinc-800 bg-zinc-950 px-4 pt-2 pb-4 space-y-1' : 'max-h-0'
      }`}>
        <Link
          to="/"
          onClick={() => setIsOpen(false)}
          className={`block px-3 py-2.5 rounded-md text-base font-medium ${
            isActive('/') ? 'bg-zinc-900 text-white' : 'text-zinc-400 hover:bg-zinc-900/50 hover:text-white'
          }`}
        >
          Overview
        </Link>
        {isAuthenticated && (
          <Link
            to="/dashboard"
            onClick={() => setIsOpen(false)}
            className={`block px-3 py-2.5 rounded-md text-base font-medium ${
              isActive('/dashboard') ? 'bg-zinc-900 text-white' : 'text-zinc-400 hover:bg-zinc-900/50 hover:text-white'
            }`}
          >
            Dashboard
          </Link>
        )}
        <Link
          to="/docs"
          onClick={() => setIsOpen(false)}
          className={`block px-3 py-2.5 rounded-md text-base font-medium ${
            isActive('/docs') ? 'bg-zinc-900 text-white' : 'text-zinc-400 hover:bg-zinc-900/50 hover:text-white'
          }`}
        >
          API Docs
        </Link>
        
        <div className="pt-4 border-t border-zinc-800">
          {isAuthenticated ? (
            <button
              onClick={() => {
                setIsOpen(false);
                logout();
              }}
              className="flex items-center justify-center gap-1.5 w-full py-2.5 px-4 rounded-md bg-rose-900/20 border border-rose-900/40 text-rose-400 text-sm font-semibold shadow-md transition-colors cursor-pointer"
            >
              Sign Out
              <LogOut className="w-4 h-4" />
            </button>
          ) : (
            <div className="space-y-2">
              <Link
                to="/login"
                onClick={() => setIsOpen(false)}
                className="block text-center w-full py-2 px-4 rounded-md border border-zinc-800 text-zinc-300 text-sm font-semibold hover:bg-zinc-900"
              >
                Sign In
              </Link>
              <Link
                to="/register"
                onClick={() => setIsOpen(false)}
                className="flex items-center justify-center gap-1.5 w-full py-2.5 px-4 rounded-md bg-indigo-600 hover:bg-indigo-700 text-white text-sm font-semibold shadow-md transition-colors"
              >
                Get Started
                <ChevronRight className="w-4 h-4" />
              </Link>
            </div>
          )}
        </div>
      </div>
    </nav>
  );
};

export default Navbar;