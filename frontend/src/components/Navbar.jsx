import React, { useState, useEffect } from 'react';
import { NavLink, useNavigate, useLocation } from 'react-router-dom';
import { LayoutDashboard, MessageSquare, Users, LogOut, Menu, X, Settings } from 'lucide-react';
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
    { name: 'Dashboard', path: '/', icon: <LayoutDashboard size={22} /> },
    { name: 'AI Assistant', path: '/assistant', icon: <MessageSquare size={22} /> },
    { name: 'Leads', path: '/leads', icon: <Users size={22} /> },
  ];

  /* ─── Desktop Slim Sidebar (icon-only, 80px) ─── */
  const desktopSidebar = (
    <nav className="hidden md:flex fixed top-0 left-0 h-screen w-20 bg-surface-card border-r border-border flex-col items-center py-6 z-30">
      {/* Brand Mark */}
      <div className="w-10 h-10 rounded-2xl bg-primary flex items-center justify-center mb-8 shadow-card flex-shrink-0">
        <span className="text-white font-bold text-lg">S</span>
      </div>

      {/* Nav Items */}
      <div className="flex-1 flex flex-col items-center gap-2">
        {navItems.map((item) => (
          <NavLink
            key={item.name}
            to={item.path}
            title={item.name}
            className={({ isActive }) =>
              `relative w-12 h-12 flex items-center justify-center rounded-2xl transition-all duration-200 group ${
                isActive
                  ? 'bg-primary text-white shadow-md'
                  : 'text-muted hover:bg-gray-100 hover:text-heading'
              }`
            }
          >
            {item.icon}
            {/* Tooltip */}
            <span className="absolute left-full ml-3 px-3 py-1.5 rounded-lg bg-heading text-white text-xs font-medium opacity-0 group-hover:opacity-100 pointer-events-none transition-opacity duration-150 whitespace-nowrap shadow-lg">
              {item.name}
            </span>
          </NavLink>
        ))}
      </div>

      {/* Bottom Section */}
      <div className="flex flex-col items-center gap-3 pt-4 border-t border-divider mt-4">
        <button
          onClick={handleLogout}
          title="Logout"
          className="w-12 h-12 flex items-center justify-center rounded-2xl text-muted hover:bg-error-light hover:text-error transition-all duration-200"
        >
          <LogOut size={20} />
        </button>
        <div
          className="w-10 h-10 rounded-full bg-primary-light flex items-center justify-center text-primary font-semibold text-sm cursor-default"
          title={user?.name || 'User'}
        >
          {user?.name?.charAt(0).toUpperCase() || 'U'}
        </div>
      </div>
    </nav>
  );

  /* ─── Mobile Slide-over Drawer ─── */
  const mobileSidebarContent = (
    <>
      <div className="h-14 flex items-center justify-between px-5 border-b border-border flex-shrink-0">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-xl bg-primary flex items-center justify-center">
            <span className="text-white font-bold text-sm">S</span>
          </div>
          <h1 className="text-lg font-semibold text-heading">SynapseSync</h1>
        </div>
        <button
          onClick={() => setMobileOpen(false)}
          className="p-1.5 rounded-xl text-muted hover:text-heading hover:bg-gray-100 transition-colors"
          aria-label="Close menu"
        >
          <X size={22} />
        </button>
      </div>
      
      <div className="flex-1 px-3 py-4 space-y-1 overflow-y-auto">
        {navItems.map((item) => (
          <NavLink
            key={item.name}
            to={item.path}
            className={({ isActive }) =>
              `flex items-center gap-3 px-4 py-3 rounded-2xl transition-all duration-200 ${
                isActive
                  ? 'bg-primary-light text-primary font-medium'
                  : 'text-body hover:bg-gray-50 hover:text-heading'
              }`
            }
          >
            {item.icon}
            <span className="text-sm">{item.name}</span>
          </NavLink>
        ))}
      </div>
      
      <div className="p-3 border-t border-border flex-shrink-0">
        <div className="flex items-center justify-between px-3 py-2">
          <div className="flex items-center gap-3 overflow-hidden">
            <div className="w-9 h-9 rounded-full bg-primary-light flex-shrink-0 flex items-center justify-center text-primary text-sm font-semibold">
              {user?.name?.charAt(0).toUpperCase() || 'U'}
            </div>
            <span className="text-sm font-medium text-heading truncate">
              {user?.name || 'User'}
            </span>
          </div>
          <button 
            onClick={handleLogout}
            className="text-muted hover:text-error transition-colors p-2 rounded-xl hover:bg-error-light"
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
      {/* Desktop slim sidebar — pushes content via ml-20 in parent */}
      {desktopSidebar}
      {/* Spacer for desktop to offset fixed sidebar */}
      <div className="hidden md:block w-20 flex-shrink-0" />

      {/* Mobile top bar */}
      <div className="md:hidden fixed top-0 left-0 right-0 z-40 h-14 bg-surface-card/95 backdrop-blur-md border-b border-border flex items-center px-4">
        <button
          onClick={() => setMobileOpen(true)}
          className="p-2 rounded-xl text-body hover:text-heading hover:bg-gray-100 transition-colors"
          aria-label="Open menu"
        >
          <Menu size={22} />
        </button>
        <div className="flex items-center gap-2 ml-3">
          <div className="w-7 h-7 rounded-lg bg-primary flex items-center justify-center">
            <span className="text-white font-bold text-xs">S</span>
          </div>
          <h1 className="text-base font-semibold text-heading">SynapseSync</h1>
        </div>
      </div>

      {/* Backdrop overlay for mobile */}
      {mobileOpen && (
        <div
          className="md:hidden fixed inset-0 z-40 bg-black/30 backdrop-blur-sm transition-opacity"
          onClick={() => setMobileOpen(false)}
        />
      )}

      {/* Mobile slide-over sidebar */}
      <nav
        className={`
          fixed md:hidden z-50
          top-0 left-0 h-full
          w-[280px]
          bg-surface-card border-r border-border
          flex flex-col
          transform transition-transform duration-300 ease-in-out
          shadow-modal
          ${mobileOpen ? 'translate-x-0' : '-translate-x-full'}
        `}
      >
        {mobileSidebarContent}
      </nav>
    </>
  );
};

export default Navbar;
