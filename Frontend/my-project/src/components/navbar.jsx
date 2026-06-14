import React , { useState } from 'react';
import { Link } from 'react-router-dom';

const Navbar = () => {
    const [isOpen, setIsOpen] = useState(false);

    return (
        <div>
            <nav className="bg-zinc-800 text-white p-4">
                <div className="container mx-auto flex justify-between items-center">
                    <Link to="/" className="text-xl font-bold">
                        My App
                    </Link>
                    <div className="hidden md:block">
                        <Link to="/" className="mx-2 hover:underline">
                            Home
                        </Link>
                        <Link to="/about" className="mx-2 hover:underline">
                            About
                        </Link>
                        <Link to="/contact" className="mx-2 hover:underline">
                            Contact
                        </Link>
                    </div>
                    <button
                        className="md:hidden text-white focus:outline-none"
                        onClick={() => setIsOpen(!isOpen)}
                    >
                        <svg
                            className="w-6 h-6"
                            fill="none"
                            stroke="currentColor"
                            viewBox="0 0 24 24"
                            xmlns="http://www.w3.org/2000/svg"
                        >
                            <path
                                strokeLinecap="round"
                                strokeLinejoin="round"
                                strokeWidth={2}
                                d={isOpen ? "M6 18L18 6M6 6l12 12" : "M4 6h16M4 12h16M4 18h16"}
                            />
                        </svg>
                    </button>
                </div>
                {isOpen && (
                    <div className="md:hidden bg-zinc-700 p-4">
                        <Link to="/" className="block py-2 hover:underline">
                            Home
                        </Link>
                        <Link to="/about" className="block py-2 hover:underline">
                            About
                        </Link>
                        <Link to="/contact" className="block py-2 hover:underline">
                            Contact
                        </Link>
                    </div>
                )}
            </nav>
        </div>
    );
};

export default Navbar;