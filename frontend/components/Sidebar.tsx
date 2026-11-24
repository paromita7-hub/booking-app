"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  LayoutDashboard,
  Building2,
  MessageSquareText,
  AlertTriangle,
  UploadCloud,
  ChevronLeft,
  ChevronRight,
  ShieldCheck,
} from "lucide-react";
import { useState } from "react";
import { cn } from "@/lib/utils";

const NAV_ITEMS = [
  { href: "/", label: "Overview", icon: LayoutDashboard },
  { href: "/properties", label: "Properties", icon: Building2 },
  { href: "/reviews", label: "Reviews Explorer", icon: MessageSquareText },
  { href: "/insights", label: "Operational Insights", icon: AlertTriangle },
  { href: "/imports", label: "Data Imports", icon: UploadCloud },
];

export function Sidebar() {
  const pathname = usePathname();
  const [collapsed, setCollapsed] = useState(false);

  return (
    <aside
      className={cn(
        "relative flex flex-col border-r border-slate-200 bg-white transition-all duration-300 min-h-screen",
        collapsed ? "w-20" : "w-64"
      )}
    >
      {/* Brand Header */}
      <div className="flex h-16 items-center justify-between px-4 border-b border-slate-100">
        {!collapsed && (
          <div className="flex flex-col">
            <span className="font-bold text-lg tracking-tight text-slate-900">
              Azzurro Hotels
            </span>
            <span className="text-xs font-medium text-slate-500">
              Review Insights & Ops
            </span>
          </div>
        )}
        {collapsed && (
          <div className="w-10 h-10 rounded-lg bg-blue-900 flex items-center justify-center text-white font-bold text-lg">
            A
          </div>
        )}
        <button
          onClick={() => setCollapsed(!collapsed)}
          className="p-1.5 rounded-md hover:bg-slate-100 text-slate-400 hover:text-slate-600 transition"
          title={collapsed ? "Expand sidebar" : "Collapse sidebar"}
        >
          {collapsed ? <ChevronRight size={18} /> : <ChevronLeft size={18} />}
        </button>
      </div>

      {/* Demo Data Banner */}
      <div className={cn("px-4 py-3 border-b border-slate-100", collapsed && "hidden")}>
        <div className="flex items-center gap-2 px-2.5 py-1.5 rounded-md bg-amber-50 border border-amber-200 text-amber-800 text-xs font-medium">
          <ShieldCheck size={14} className="text-amber-600 flex-shrink-0" />
          <span>Demo Data Mode Active</span>
        </div>
      </div>

      {/* Nav items */}
      <nav className="flex-1 px-3 py-4 space-y-1.5">
        {NAV_ITEMS.map((item) => {
          const isActive = pathname === item.href;
          const Icon = item.icon;
          return (
            <Link
              key={item.href}
              href={item.href}
              className={cn(
                "flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors",
                isActive
                  ? "bg-blue-50 text-blue-900 font-semibold"
                  : "text-slate-600 hover:bg-slate-50 hover:text-slate-900"
              )}
            >
              <Icon
                size={20}
                className={cn(
                  isActive ? "text-blue-700" : "text-slate-400 group-hover:text-slate-600"
                )}
              />
              {!collapsed && <span>{item.label}</span>}
            </Link>
          );
        })}
      </nav>

      {/* Footer / Property Info */}
      {!collapsed && (
        <div className="p-4 border-t border-slate-100 text-xs text-slate-400">
          <p className="font-medium text-slate-600 mb-0.5">4 Properties Monitored</p>
          <p>Sydney (AEST/AEDT Timezone)</p>
          <p className="mt-2 text-[11px] text-slate-400">v1.0.0 Production Build</p>
        </div>
      )}
    </aside>
  );
}
