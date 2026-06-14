import React from 'react';

const Hero = () =>{
    return (
        <section className="hero flex flex-col items-center justify-center text-center py-20">
            <h1 className="text-4xl font-bold mb-4">Welcome to My App</h1>
            <p className="text-lg mb-8">This is a simple hero section to introduce your app.</p>
            <button className="bg-blue-500 text-white px-6 py-3 rounded hover:bg-blue-600">
                Get Started
            </button>
        </section>
    );
}

export default Hero;