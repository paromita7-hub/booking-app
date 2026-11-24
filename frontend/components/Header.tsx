"use client";

import { useEffect, useState } from "react";
import { Property } from "@/types";
import { api } from "@/lib/api";
import { Building2, Globe, Clock } from "lucide-react";

interface HeaderProps {
  selectedPropertyId: number | null;
  onPropertyChange: (id: number | null) => void;
}

export function Header({ selectedPropertyId, onPropertyChange }: HeaderProps) {
  const [properties, setProperties] = useState<Property[]>([]);
  const [sydneyTime, setSydneyTime] = useState<string>("");

  useEffect(() => {
    api.getProperties().then(setProperties).catch(console.error);

    // Update Sydney clock
    const updateTime = () => {
      const timeStr = new Intl.DateTimeFormat("en-AU", {
        timeZone: "Australia/Sydney",
        weekday: "short",
        day: "numeric",
        month: "short",
        hour: "2-digit",
        minute: "2-digit",
      }).format(new Date());
      setSydneyTime(timeStr);
    };
    updateTime();
    const interval = setInterval(updateTime, 30000);
    return () => clearInterval(interval);
  }, []);

  return (
    <header className="h-16 border-b border-slate-200 bg-white px-8 flex items-center justify-between sticky top-0 z-10 shadow-sm">
      <div className="flex items-center gap-4">
        <div className="flex items-center gap-2 text-slate-700 text-sm font-medium">
          <Building2 size={18} className="text-blue-800" />
          <span>Active Scope:</span>
        </div>
        <select
          value={selectedPropertyId || ""}
          onChange={(e) => {
            const val = e.target.value;
            onPropertyChange(val ? parseInt(val, 10) : null);
          }}
          className="border border-slate-300 rounded-lg px-3 py-1.5 text-sm bg-white text-slate-800 focus:outline-none focus:ring-2 focus:ring-blue-500 font-medium"
        >
          <option value="">All 4 Azzurro Properties</option>
          {properties.map((p) => (
            <option key={p.id} value={p.id}>
              {p.name} ({p.location.split(",")[0]})
            </option>
          ))}
        </select>
      </div>

      <div className="flex items-center gap-4 text-xs text-slate-500">
        <div className="flex items-center gap-1.5 bg-slate-50 px-2.5 py-1 rounded-md border border-slate-200">
          <Clock size={14} className="text-slate-400" />
          <span>Sydney: {sydneyTime || "AEST"}</span>
        </div>
        <div className="flex items-center gap-1.5 bg-blue-50 text-blue-800 px-2.5 py-1 rounded-md border border-blue-200 font-medium">
          <Globe size={14} className="text-blue-600" />
          <span>Booking.com Connected</span>
        </div>
      </div>
    </header>
  );
}
