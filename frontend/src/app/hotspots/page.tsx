'use client';

import { useEffect, useState } from 'react';
import { api } from '@/lib/api';
import { MapPin, Layers } from 'lucide-react';

const CAUSE_COLORS = [
  '#3b82f6', '#f97316', '#22c55e', '#ef4444', '#8b5cf6',
  '#ec4899', '#14b8a6', '#eab308', '#6366f1', '#84cc16', '#06b6d4'
];

export default function HotspotsPage() {
  const [causes, setCauses] = useState<Record<string, number>>({});
  const [selectedCause, setSelectedCause] = useState<string>('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.getHotspots().then((res) => {
      const d = res as { causes: Record<string, number> };
      setCauses(d.causes);
      const keys = Object.keys(d.causes);
      if (keys.length > 0) setSelectedCause(keys[0]);
    }).catch(console.error).finally(() => setLoading(false));
  }, []);

  if (loading) return <LoadingHotspots />;

  const causeList = Object.entries(causes).sort((a, b) => b[1] - a[1]);
  const totalClusters = causeList.reduce((acc, [, v]) => acc + v, 0);

  return (
    <div className="space-y-6 animate-fade-in">
      <div>
        <h1 className="text-2xl font-bold text-slate-100">Hotspot Analysis</h1>
        <p className="text-slate-400 mt-1">Spatial clustering of events by cause type</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Cause list */}
        <div className="lg:col-span-1 space-y-3">
          {causeList.map(([cause, count], i) => (
            <button
              key={cause}
              onClick={() => setSelectedCause(cause)}
              className={`w-full card-hover flex items-center gap-3 !p-3.5
                ${selectedCause === cause ? 'ring-1 ring-primary-500/50 bg-surface-lighter/50' : ''}`}
            >
              <div className="w-3 h-3 rounded-full shrink-0" style={{ background: CAUSE_COLORS[i % CAUSE_COLORS.length] }} />
              <div className="flex-1 min-w-0 text-left">
                <p className="text-sm font-medium text-slate-200 truncate capitalize">{cause.replace(/_/g, ' ')}</p>
                <p className="text-xs text-slate-500">{count} cluster{count > 1 ? 's' : ''}</p>
              </div>
              <span className="text-xs font-semibold text-slate-400">{count}</span>
            </button>
          ))}
        </div>

        {/* Detail */}
        <div className="lg:col-span-2">
          <div className="card">
            <h3 className="text-sm font-semibold text-slate-300 mb-4 flex items-center gap-2">
              <MapPin size={16} className="text-primary-400" />
              {selectedCause ? selectedCause.replace(/_/g, ' ') : 'Select a cause'} — Hotspot Clusters
            </h3>
            {!selectedCause ? (
              <div className="flex flex-col items-center justify-center h-64 text-slate-500">
                <Layers size={40} className="mb-3 opacity-30" />
                <p className="text-sm">Select an event cause to view hotspots</p>
              </div>
            ) : (
              <div className="bg-surface-lighter/30 rounded-lg p-6 text-center">
                <div className="text-5xl font-bold text-primary-400 mb-2">{causes[selectedCause]}</div>
                <p className="text-sm text-slate-400">hotspot clusters detected</p>
                <p className="text-xs text-slate-500 mt-4">
                  These clusters represent recurring spatial patterns where
                  <span className="text-slate-300 capitalize"> {selectedCause.replace(/_/g, ' ')} </span>
                  events frequently occur. Each cluster groups nearby events using DBSCAN density-based clustering.
                </p>
              </div>
            )}
          </div>

          {/* Summary card */}
          <div className="card mt-4">
            <h3 className="text-sm font-semibold text-slate-300 mb-4">Summary</h3>
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
              <SummaryBox value={causeList.length} label="Event Causes" />
              <SummaryBox value={totalClusters} label="Total Clusters" />
              <SummaryBox value={causeList[0]?.[1] || 0} label="Most Clusters" sub={causeList[0]?.[0]?.replace(/_/g, ' ') || ''} />
              <SummaryBox value="11" label="Algorithm" sub="DBSCAN (eps=0.008)" />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

function SummaryBox({ value, label, sub }: { value: number | string; label: string; sub?: string }) {
  return (
    <div className="bg-surface-lighter rounded-lg p-4 text-center">
      <p className="text-xl font-bold text-slate-100">{value}</p>
      <p className="text-xs text-slate-400 mt-1">{label}</p>
      {sub && <p className="text-[10px] text-slate-500 mt-0.5 truncate">{sub}</p>}
    </div>
  );
}

function LoadingHotspots() {
  return (
    <div className="space-y-6 animate-pulse">
      <div className="h-8 w-48 bg-surface-lighter rounded-lg" />
      <div className="grid grid-cols-3 gap-6">
        <div className="col-span-1 space-y-3">
          {[1, 2, 3, 4, 5].map(i => <div key={i} className="h-14 bg-surface-lighter rounded-lg" />)}
        </div>
        <div className="col-span-2 h-80 bg-surface-lighter rounded-xl" />
      </div>
    </div>
  );
}
