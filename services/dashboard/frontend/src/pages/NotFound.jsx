import React from 'react';
import { Link } from 'react-router-dom';

const NotFound = () => {
  return (
    <div className="min-h-screen pt-16 pb-12 flex flex-col bg-white">
      <main className="flex-grow flex flex-col justify-center max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex-shrink-0 flex justify-center">
          <a href="/" className="inline-flex">
            <span className="sr-only">Dropshipping Crew AI</span>
            <img
              className="h-12 w-auto"
              src="/logo.svg"
              alt="Logo"
            />
          </a>
        </div>
        <div className="py-16">
          <div className="text-center">
            <p className="text-sm font-semibold text-primary-600 uppercase tracking-wide">Erreur 404</p>
            <h1 className="mt-2 text-4xl font-extrabold text-gray-900 tracking-tight sm:text-5xl">Page non trouvée</h1>
            <p className="mt-2 text-base text-gray-500">Désolé, nous n'avons pas pu trouver la page que vous recherchez.</p>
            <div className="mt-6">
              <Link to="/" className="text-base font-medium text-primary-600 hover:text-primary-500">
                Retour à l'accueil<span aria-hidden="true"> &rarr;</span>
              </Link>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
};

export default NotFound;
