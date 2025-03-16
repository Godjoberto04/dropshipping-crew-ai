import React, { useState } from 'react';
import { Link, Outlet, useLocation } from 'react-router-dom';
import {
  HomeIcon,
  ChartBarIcon,
  DocumentTextIcon,
  ShoppingBagIcon,
  CogIcon,
  BellIcon,
  UserCircleIcon,
  ArrowsUpDownIcon,
  ShoppingCartIcon
} from '@heroicons/react/24/outline';

const navigation = [
  { name: 'Vue d\'ensemble', icon: HomeIcon, href: '/' },
  { name: 'Data Analyzer', icon: ChartBarIcon, href: '/data-analyzer' },
  { name: 'Website Builder', icon: DocumentTextIcon, href: '/website-builder' },
  { name: 'Content Generator', icon: DocumentTextIcon, href: '/content-generator' },
  { name: 'Order Manager', icon: ShoppingBagIcon, href: '/order-manager' },
  { name: 'Site Updater', icon: ArrowsUpDownIcon, href: '/site-updater' },
  { name: 'Boutiques Shopify', icon: ShoppingCartIcon, href: '/shopify-stores' },
  { name: 'Configuration', icon: CogIcon, href: '/settings' },
];

const DashboardLayout = () => {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const location = useLocation();

  return (
    <div className="min-h-screen bg-gray-100">
      {/* Mobile sidebar */}
      <div
        className={`fixed inset-0 z-40 flex md:hidden ${
          sidebarOpen ? 'visible' : 'invisible'
        }`}
        role="dialog"
        aria-modal="true"
      >
        <div
          className={`fixed inset-0 bg-gray-600 bg-opacity-75 transition-opacity ${
            sidebarOpen ? 'opacity-100 ease-out' : 'opacity-0 ease-in'
          }`}
          aria-hidden="true"
        ></div>

        <div
          className={`relative flex-1 flex flex-col max-w-xs w-full pt-5 pb-4 bg-primary-800 transform ${
            sidebarOpen ? 'translate-x-0' : '-translate-x-full'
          } transition-transform`}
        >
          <div className="absolute top-0 right-0 -mr-12 pt-2">
            <button
              type="button"
              className="ml-1 flex items-center justify-center h-10 w-10 rounded-full focus:outline-none focus:ring-2 focus:ring-inset focus:ring-white"
              onClick={() => setSidebarOpen(false)}
            >
              <span className="sr-only">Fermer le menu</span>
              <svg
                className="h-6 w-6 text-white"
                xmlns="http://www.w3.org/2000/svg"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
                aria-hidden="true"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth="2"
                  d="M6 18L18 6M6 6l12 12"
                />
              </svg>
            </button>
          </div>

          <MobileSidebar location={location} setSidebarOpen={setSidebarOpen} />
        </div>

        <div className="flex-shrink-0 w-14" aria-hidden="true">
          {/* Dummy element to force sidebar to shrink to fit close icon */}
        </div>
      </div>

      {/* Static sidebar for desktop */}
      <div className="hidden md:flex md:w-64 md:flex-col md:fixed md:inset-y-0">
        <div className="flex-1 flex flex-col min-h-0 bg-primary-800">
          <DesktopSidebar location={location} />
        </div>
      </div>

      {/* Content area */}
      <div className="md:pl-64 flex flex-col flex-1">
        <div className="sticky top-0 z-10 flex-shrink-0 flex h-16 bg-white shadow">
          <button
            type="button"
            className="px-4 border-r border-gray-200 text-gray-500 focus:outline-none focus:ring-2 focus:ring-inset focus:ring-primary-500 md:hidden"
            onClick={() => setSidebarOpen(true)}
          >
            <span className="sr-only">Ouvrir le menu</span>
            <svg
              className="h-6 w-6"
              xmlns="http://www.w3.org/2000/svg"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
              aria-hidden="true"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth="2"
                d="M4 6h16M4 12h16M4 18h16"
              />
            </svg>
          </button>

          <div className="flex-1 px-4 flex justify-between">
            <div className="flex-1 flex">
              <div className="w-full flex items-center">
                <h1 className="text-2xl font-semibold text-gray-900">
                  Dashboard Dropshipping-Crew-AI
                </h1>
              </div>
            </div>
            <div className="ml-4 flex items-center md:ml-6">
              <button
                type="button"
                className="bg-white p-1 rounded-full text-gray-400 hover:text-gray-500 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
              >
                <span className="sr-only">Voir les notifications</span>
                <BellIcon className="h-6 w-6" aria-hidden="true" />
              </button>

              {/* Profile dropdown */}
              <div className="ml-3 relative">
                <div>
                  <button
                    type="button"
                    className="max-w-xs bg-white flex items-center text-sm rounded-full focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
                    id="user-menu-button"
                    aria-expanded="false"
                    aria-haspopup="true"
                  >
                    <span className="sr-only">Ouvrir le menu utilisateur</span>
                    <UserCircleIcon className="h-8 w-8 text-gray-400" />
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>

        <main className="flex-1">
          <div className="py-6">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 md:px-8">
              <Outlet />
            </div>
          </div>
        </main>
      </div>
    </div>
  );
};

const MobileSidebar = ({ location, setSidebarOpen }) => (
  <div className="flex-1 h-0 pt-5 pb-4 overflow-y-auto">
    <div className="flex-shrink-0 flex items-center px-4">
      <img
        className="h-8 w-auto"
        src="/logo.svg"
        alt="Dropshipping Crew AI"
      />
      <span className="ml-2 text-white text-xl font-bold">Dropshipping Crew AI</span>
    </div>
    <nav className="mt-5 px-2 space-y-1">
      {navigation.map((item) => (
        <Link
          key={item.name}
          to={item.href}
          className={`${
            location.pathname === item.href
              ? 'bg-primary-900 text-white'
              : 'text-white hover:bg-primary-700'
          } group flex items-center px-2 py-2 text-base font-medium rounded-md`}
          onClick={() => setSidebarOpen(false)}
        >
          <item.icon
            className="mr-4 h-6 w-6 text-primary-300"
            aria-hidden="true"
          />
          {item.name}
        </Link>
      ))}
    </nav>
  </div>
);

const DesktopSidebar = ({ location }) => (
  <div className="flex-1 flex flex-col pt-5 pb-4 overflow-y-auto">
    <div className="flex items-center flex-shrink-0 px-4">
      <img
        className="h-8 w-auto"
        src="/logo.svg"
        alt="Dropshipping Crew AI"
      />
      <span className="ml-2 text-white text-xl font-bold">Dropshipping Crew AI</span>
    </div>
    <nav className="mt-5 flex-1 px-2 space-y-1">
      {navigation.map((item) => (
        <Link
          key={item.name}
          to={item.href}
          className={`${
            location.pathname === item.href
              ? 'bg-primary-900 text-white'
              : 'text-white hover:bg-primary-700'
          } group flex items-center px-2 py-2 text-sm font-medium rounded-md`}
        >
          <item.icon
            className="mr-3 h-6 w-6 text-primary-300"
            aria-hidden="true"
          />
          {item.name}
        </Link>
      ))}
    </nav>
  </div>
);

export default DashboardLayout;
