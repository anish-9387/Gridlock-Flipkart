'use client';

import { useState } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import {
  LayoutDashboard, Radar, MapPin, AlertTriangle, Search,
  Crosshair, ClipboardList, ChevronLeft, ChevronRight, Menu
} from 'lucide-react';

const links = [
  { href: '/', label: 'Dashboard', icon: LayoutDashboard },
  { href: '/predict', label: 'Impact Prediction', icon: Radar },
  { href: '/hotspots', label: 'Hotspot Analysis', icon: MapPin },
  { href: '/vulnerability', label: 'Junction Vulnerability', icon: AlertTriangle },
  { href: '/similarity', label: 'Event Similarity', icon: Search },
  { href: '/autopsy', label: 'Cascade Autopsy', icon: Crosshair },
  { href: '/resources', label: 'Resource Planning', icon: ClipboardList },
];

export default function Sidebar() {
  const pathname = usePathname();
  const [collapsed, setCollapsed] = useState(false);

  return (
    <>
      {/* Mobile overlay */}
      <div className="fixed inset-0 bg-black/50 z-40 lg:hidden" />

      <aside className={`fixed top-0 left-0 z-50 h-full bg-surface-light border-r border-surface-border
        transition-all duration-300 flex flex-col
        ${collapsed ? 'w-[72px]' : 'w-64'}`}>

        {/* Logo */}
        <div className="flex items-center gap-3 px-5 h-16 border-b border-surface-border shrink-0">
          <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-primary-500 to-primary-700
            flex items-center justify-center text-white font-bold text-sm shrink-0">
            CQ
          </div>
          {!collapsed && (
            <div className="min-w-0">
              <p className="text-sm font-semibold text-slate-100 truncate">CascadeIQ</p>
              <p className="text-[10px] text-slate-500 truncate">Gridlock-Flipkart 2.0</p>
            </div>
          )}
        </div>

        {/* Nav */}
        <nav className="flex-1 overflow-y-auto p-3 space-y-1">
          {links.map(({ href, label, icon: Icon }) => {
            const active = pathname === href;
            return (
              <Link
                key={href}
                href={href}
                className={active ? 'sidebar-link-active' : 'sidebar-link'}
                title={collapsed ? label : undefined}
              >
                <Icon size={20} className="shrink-0" />
                {!collapsed && <span className="truncate">{label}</span>}
              </Link>
            );
          })}
        </nav>

        {/* Collapse toggle */}
        <div className="p-3 border-t border-surface-border">
          <button
            onClick={() => setCollapsed(!collapsed)}
            className="sidebar-link w-full"
          >
            {collapsed ? <ChevronRight size={20} /> : <ChevronLeft size={20} />}
            {!collapsed && <span>Collapse</span>}
          </button>
        </div>
      </aside>
    </>
  );
}
