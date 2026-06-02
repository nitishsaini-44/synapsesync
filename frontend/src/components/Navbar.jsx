import React, { useState, useEffect } from 'react';
import { NavLink, useNavigate, useLocation } from 'react-router-dom';
import { LayoutDashboard, MessageSquare, Users, LogOut, Menu, X } from 'lucide-react';
import { useAuth } from './AuthContext';

const Navbar = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [mobileOpen, setMobileOpen] = useState(false);

  // Close mobile nav on route change
  useEffect(() => {
    setMobileOpen(false);
  }, [location.pathname]);

  // Prevent body scroll when mobile menu is open
  useEffect(() => {
    if (mobileOpen) {
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = '';
    }
    return () => { document.body.style.overflow = ''; };
  }, [mobileOpen]);

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const navItems = [
    { name: 'Dashboard', path: '/', icon: <LayoutDashboard size={20} /> },
    { name: 'AI Assistant', path: '/assistant', icon: <MessageSquare size={20} /> },
    { name: 'Leads', path: '/leads', icon: <Users size={20} /> },
  ];

  const sidebarContent = (
    <>
      <div className="h-16 md:h-20 flex items-center justify-between px-5 md:px-8 border-b border-slate-700 flex-shrink-0">
        <h1 className="text-xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-primary to-purple-400">
          SynapseSync
        </h1>
        {/* Close button visible only on mobile */}
        <button
          onClick={() => setMobileOpen(false)}
          className="md:hidden p-1.5 rounded-lg text-slate-400 hover:text-slate-200 hover:bg-dark-surfaceHover transition-colors"
          aria-label="Close menu"
        >
          <X size={22} />
        </button>
      </div>
      
      <div className="flex-1 px-3 md:px-4 py-4 md:py-6 space-y-1 md:space-y-2 overflow-y-auto">
        {navItems.map((item) => (
          <NavLink
            key={item.name}
            to={item.path}
            className={({ isActive }) =>
              `flex items-center space-x-3 px-4 py-3 rounded-lg transition-all duration-200 ${
                isActive
                  ? 'bg-primary/10 text-primary font-medium'
                  : 'text-slate-400 hover:bg-dark-surfaceHover hover:text-slate-200'
              }`
            }
          >
            {item.icon}
            <span>{item.name}</span>
          </NavLink>
        ))}
      </div>
      
      <div className="p-3 md:p-4 border-t border-slate-700 flex-shrink-0">
        <div className="flex items-center justify-between px-3 md:px-4 py-2">
          <div className="flex items-center space-x-3 overflow-hidden">
            <div className="w-8 h-8 rounded-full bg-gradient-to-br from-primary to-purple-500 flex-shrink-0 flex items-center justify-center text-sm font-bold">
              {user?.name?.charAt(0).toUpperCase() || 'U'}
            </div>
            <span className="text-sm font-medium text-slate-300 truncate">
              {user?.name || 'User'}
            </span>
          </div>
          <button 
            onClick={handleLogout}
            className="text-slate-500 hover:text-danger transition-colors p-2 rounded-lg hover:bg-danger/10"
            title="Logout"
          >
            <LogOut size={18} />
          </button>
        </div>
      </div>
    </>
  );

  return (
    <>
      {/* Mobile top bar with hamburger */}
      <div className="md:hidden fixed top-0 left-0 right-0 z-40 h-14 bg-dark-surface/95 backdrop-blur-md border-b border-slate-700 flex items-center px-4">
        <button
          onClick={() => setMobileOpen(true)}
          className="p-2 rounded-lg text-slate-300 hover:text-slate-100 hover:bg-dark-surfaceHover transition-colors"
          aria-label="Open menu"
        >
          <Menu size={22} />
        </button>
        <h1 className="ml-3 text-lg font-bold bg-clip-text text-transparent bg-gradient-to-r from-primary to-purple-400">
          SynapseSync
        </h1>
      </div>

      {/* Backdrop overlay for mobile */}
      {mobileOpen && (
        <div
          className="md:hidden fixed inset-0 z-40 bg-black/60 backdrop-blur-sm transition-opacity"
          onClick={() => setMobileOpen(false)}
        />
      )}

      {/* Sidebar — fixed on desktop, slide-over on mobile */}
      <nav
        className={`
          fixed md:relative z-50 md:z-auto
          top-0 left-0 h-full
          w-[280px] md:w-64
          bg-dark-surface border-r border-slate-700
          flex flex-col
          transform transition-transform duration-300 ease-in-out
          ${mobileOpen ? 'translate-x-0' : '-translate-x-full md:translate-x-0'}
        `}
      >
        {sidebarContent}
      </nav>
    </>
  );
};

export default Navbar;
