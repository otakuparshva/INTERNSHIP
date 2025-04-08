import { Fragment } from 'react';
import { Outlet, Link, useLocation } from 'react-router-dom';
import { Disclosure, Menu, Transition } from '@headlessui/react';
import { Bars3Icon, XMarkIcon } from '@heroicons/react/24/outline';
import { useAuthStore } from '@/store/auth';

const navigation = [
  { name: 'Home', href: '/', current: true },
  { name: 'Jobs', href: '/jobs', current: false },
];

function classNames(...classes) {
  return classes.filter(Boolean).join(' ');
}

const Layout = () => {
  const location = useLocation();
  const { user, isAuthenticated, logout } = useAuthStore();

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 via-gray-100 to-gray-200">
      <Disclosure as="nav" className="bg-white/90 backdrop-blur-md shadow-sm sticky top-0 z-50 border-b border-gray-200">
        {({ open }) => (
          <>
            <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
              <div className="flex h-16 justify-between">
                <div className="flex">
                  <div className="flex flex-shrink-0 items-center">
                    <Link to="/" className="text-2xl font-bold bg-gradient-to-r from-blue-600 via-indigo-600 to-purple-600 bg-clip-text text-transparent hover:opacity-80 transition-opacity duration-200">
                      AI Recruitment
                    </Link>
                  </div>
                  <div className="hidden sm:ml-6 sm:flex sm:space-x-8">
                    {navigation.map((item) => (
                      <Link
                        key={item.name}
                        to={item.href}
                        className={classNames(
                          location.pathname === item.href
                            ? 'border-blue-500 text-gray-900'
                            : 'border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700',
                          'inline-flex items-center border-b-2 px-1 pt-1 text-sm font-medium transition-all duration-200 hover:scale-105'
                        )}
                      >
                        {item.name}
                      </Link>
                    ))}
                  </div>
                </div>
                <div className="hidden sm:ml-6 sm:flex sm:items-center">
                  {isAuthenticated ? (
                    <Menu as="div" className="relative ml-3">
                      <div>
                        <Menu.Button className="flex rounded-full bg-white text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 transition-all duration-200 hover:shadow-md hover:scale-105">
                          <span className="sr-only">Open user menu</span>
                          <div className="h-8 w-8 rounded-full bg-gradient-to-r from-blue-500 via-indigo-500 to-purple-500 flex items-center justify-center">
                            <span className="text-white font-medium">
                              {user?.email?.[0]?.toUpperCase()}
                            </span>
                          </div>
                        </Menu.Button>
                      </div>
                      <Transition
                        as={Fragment}
                        enter="transition ease-out duration-200"
                        enterFrom="transform opacity-0 scale-95"
                        enterTo="transform opacity-100 scale-100"
                        leave="transition ease-in duration-75"
                        leaveFrom="transform opacity-100 scale-100"
                        leaveTo="transform opacity-0 scale-95"
                      >
                        <Menu.Items className="absolute right-0 z-10 mt-2 w-48 origin-top-right rounded-md bg-white py-1 shadow-lg ring-1 ring-black ring-opacity-5 focus:outline-none">
                          <Menu.Item>
                            {({ active }) => (
                              <Link
                                to={`/${user?.role}`}
                                className={classNames(
                                  active ? 'bg-gray-50' : '',
                                  'block px-4 py-2 text-sm text-gray-700 transition-colors duration-200'
                                )}
                              >
                                Dashboard
                              </Link>
                            )}
                          </Menu.Item>
                          <Menu.Item>
                            {({ active }) => (
                              <button
                                onClick={logout}
                                className={classNames(
                                  active ? 'bg-gray-50' : '',
                                  'block w-full text-left px-4 py-2 text-sm text-gray-700 transition-colors duration-200'
                                )}
                              >
                                Sign out
                              </button>
                            )}
                          </Menu.Item>
                        </Menu.Items>
                      </Transition>
                    </Menu>
                  ) : (
                    <div className="space-x-4">
                      <Link
                        to="/login"
                        className="inline-flex items-center rounded-md bg-gradient-to-r from-blue-600 via-indigo-600 to-purple-600 px-4 py-2 text-sm font-medium text-white shadow-sm hover:from-blue-700 hover:via-indigo-700 hover:to-purple-700 transition-all duration-200 hover:scale-105"
                      >
                        Sign in
                      </Link>
                      <Link
                        to="/register"
                        className="inline-flex items-center rounded-md border border-gray-300 bg-white px-4 py-2 text-sm font-medium text-gray-700 shadow-sm hover:bg-gray-50 transition-all duration-200 hover:scale-105"
                      >
                        Register
                      </Link>
                    </div>
                  )}
                </div>
                <div className="-mr-2 flex items-center sm:hidden">
                  <Disclosure.Button className="inline-flex items-center justify-center rounded-md bg-white p-2 text-gray-400 hover:bg-gray-100 hover:text-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 transition-all duration-200">
                    <span className="sr-only">Open main menu</span>
                    {open ? (
                      <XMarkIcon className="block h-6 w-6" aria-hidden="true" />
                    ) : (
                      <Bars3Icon className="block h-6 w-6" aria-hidden="true" />
                    )}
                  </Disclosure.Button>
                </div>
              </div>
            </div>

            <Disclosure.Panel className="sm:hidden">
              <div className="space-y-1 pb-3 pt-2">
                {navigation.map((item) => (
                  <Disclosure.Button
                    key={item.name}
                    as={Link}
                    to={item.href}
                    className={classNames(
                      location.pathname === item.href
                        ? 'bg-blue-50 border-blue-500 text-blue-700'
                        : 'border-transparent text-gray-600 hover:bg-gray-50 hover:border-gray-300 hover:text-gray-800',
                      'block border-l-4 py-2 pl-3 pr-4 text-base font-medium transition-colors duration-200'
                    )}
                  >
                    {item.name}
                  </Disclosure.Button>
                ))}
              </div>
              {isAuthenticated ? (
                <div className="border-t border-gray-200 pb-3 pt-4">
                  <div className="flex items-center px-4">
                    <div className="flex-shrink-0">
                      <div className="h-10 w-10 rounded-full bg-gradient-to-r from-blue-500 via-indigo-500 to-purple-500 flex items-center justify-center">
                        <span className="text-white font-medium">
                          {user?.email?.[0]?.toUpperCase()}
                        </span>
                      </div>
                    </div>
                    <div className="ml-3">
                      <div className="text-base font-medium text-gray-800">
                        {user?.email}
                      </div>
                      <div className="text-sm font-medium text-gray-500">
                        {user?.role}
                      </div>
                    </div>
                  </div>
                  <div className="mt-3 space-y-1">
                    <Disclosure.Button
                      as={Link}
                      to={`/${user?.role}`}
                      className="block px-4 py-2 text-base font-medium text-gray-500 hover:bg-gray-50 hover:text-gray-800 transition-colors duration-200"
                    >
                      Dashboard
                    </Disclosure.Button>
                    <Disclosure.Button
                      as="button"
                      onClick={logout}
                      className="block w-full text-left px-4 py-2 text-base font-medium text-gray-500 hover:bg-gray-50 hover:text-gray-800 transition-colors duration-200"
                    >
                      Sign out
                    </Disclosure.Button>
                  </div>
                </div>
              ) : (
                <div className="border-t border-gray-200 pb-3 pt-4">
                  <div className="space-y-1">
                    <Disclosure.Button
                      as={Link}
                      to="/login"
                      className="block px-4 py-2 text-base font-medium text-gray-500 hover:bg-gray-50 hover:text-gray-800 transition-colors duration-200"
                    >
                      Sign in
                    </Disclosure.Button>
                    <Disclosure.Button
                      as={Link}
                      to="/register"
                      className="block px-4 py-2 text-base font-medium text-gray-500 hover:bg-gray-50 hover:text-gray-800 transition-colors duration-200"
                    >
                      Register
                    </Disclosure.Button>
                  </div>
                </div>
              )}
            </Disclosure.Panel>
          </>
        )}
      </Disclosure>

      <main className="py-6">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <Outlet />
        </div>
      </main>
    </div>
  );
};

export default Layout; 