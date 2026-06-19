'use client';

import { useEffect, useState } from 'react';
import { api } from '@/lib/api';
import type { AutopsyEvent, AutopsyResponse } from '@/types';
import { Crosshair, Clock, Shield, AlertTriangle, Play, Zap } from 'lucide-react';

export default function AutopsyPage() {
  const [events, setEvents] = useState<AutopsyEvent[]>([]);
  const [selectedId, setSelectedId] = useState<string>('');
  const [result, setResult] = useState<AutopsyResponse | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    api.getEventsForAutopsy(100).then(r => {
      setEvents(r.events);
      if (r.events.length > 0) setSelectedId(r.events[0].id);
    }).catch(console.error);
  }, []);

  const runAutopsy = async () => {
    if (!selectedId) return;
    setLoading(true);
    try {
      const r = await api.runAutopsy(selectedId);
      setResult(r);
    } catch (err) {
      console.error(err);
    }
    setLoading(false);
  };

  const getStatusColor = (impactLabel: string) => {
    return { Low: '#22c55e', Medium: '#eab308', High: '#f97316', Critical: '#ef4444' }[impactLabel] || '#94a3b8';
  };

  return (
    <div className="space-y-6 animate-fade-in">
      <div>
        <h1 className="text-2xl font-bold text-slate-100">Cascade Autopsy</h1>
        <p className="text-slate-400 mt-1">Find the exact decision window where intervention could have prevented escalation</p>
      </div>

      {/* Selection */}
      <div className="card flex flex-wrap items-end gap-4">
        <div className="flex-1 min-w-[250px]">
          <label className="text-xs font-medium text-slate-400 mb-1.5 block">Select Historical Event</label>
          <select className="select-field" value={selectedId} onChange={e => { setSelectedId(e.target.value); setResult(null); }}>
            {events.map(e => (
              <option key={e.id} value={e.id}>
                [{e.id}] {e.event_cause} @ {e.junction || '?'} ({e.resolution_minutes.toFixed(0)} min)
              </option>
            ))}
          </select>
        </div>
        <button onClick={runAutopsy} disabled={loading || !selectedId} className="btn-primary">
          <Play size={16} /> {loading ? 'Analyzing...' : 'Run Cascade Autopsy'}
        </button>
      </div>

      {loading && (
        <div className="card flex items-center justify-center py-12">
          <div className="w-8 h-8 border-2 border-primary-500 border-t-transparent rounded-full animate-spin" />
          <span className="ml-3 text-sm text-slate-400">Running counterfactual simulation...</span>
        </div>
      )}

      {result && (
        <>
          {/* Event Info */}
          <div className="card">
            <div className="flex items-center gap-3 mb-4">
              <div className="w-3 h-3 rounded-full" style={{ background: getStatusColor(result.event.impact_label) }} />
              <div>
                <h3 className="text-sm font-semibold text-slate-200 capitalize">{result.event.event_cause}</h3>
                <p className="text-xs text-slate-400">{result.event.junction || 'N/A'} · {result.event.priority} priority</p>
              </div>
              <span className="ml-auto text-xs text-slate-500">
                Resolution: {result.event.resolution_minutes.toFixed(0)} min · {result.event.impact_label}
              </span>
            </div>
          </div>

          {result.autopsy ? (
            <>
              {/* Autopsy Results */}
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                <AutopsyCard icon={Crosshair} value={result.autopsy.point_of_no_return_time}
                  label="Point of No Return" sub={`${result.autopsy.point_of_no_return_minutes} min after start`}
                  color="#ef4444" />
                <AutopsyCard icon={Zap} value={`${result.autopsy.decision_window_minutes} min`}
                  label="Decision Window" sub="Intervene here!" color="#f97316" />
                <AutopsyCard icon={Clock} value={`${result.autopsy.potential_delay_saved} min`}
                  label="Potential Delay Saved" sub="~60% reduction" color="#22c55e" />
              </div>

              {/* Timeline */}
              <div className="card">
                <h3 className="text-sm font-semibold text-slate-300 mb-4">Reality vs Counterfactual</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div>
                    <h4 className="text-xs font-semibold text-red-400 uppercase tracking-wider mb-3">Reality</h4>
                    <div className="space-y-2">
                      <TimelineDot time={result.autopsy.event_start} label="Event Started" color="#3b82f6" />
                      <TimelineDot time={result.autopsy.point_of_no_return_time} label="Point of No Return (missed)" color="#ef4444" />
                      <TimelineDot time="Resolved" label={`Gridlock at +${result.autopsy.actual_resolution_minutes} min`} color="#ef4444" last />
                    </div>
                  </div>
                  <div>
                    <h4 className="text-xs font-semibold text-emerald-400 uppercase tracking-wider mb-3">Counterfactual (What If)</h4>
                    <div className="space-y-2">
                      <TimelineDot time={result.autopsy.event_start} label="Event Started" color="#3b82f6" />
                      <TimelineDot time={(() => {
                        const d = new Date(result.autopsy.event_start_dt);
                        d.setMinutes(d.getMinutes() + result.autopsy.point_of_no_return_minutes - 5);
                        return d.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit', hour12: false });
                      })()} label="Intervention Activated" color="#f97316" />
                      <TimelineDot time={result.autopsy.point_of_no_return_time} label="Cascade Stopped" color="#22c55e" />
                      <TimelineDot time="Resolved" label={`Normal flow at +${result.autopsy.potential_delay_saved} min`} color="#22c55e" last />
                    </div>
                  </div>
                </div>
              </div>
            </>
          ) : (
            <div className="card text-center py-8">
              <AlertTriangle size={32} className="mx-auto mb-3 text-slate-500" />
              <p className="text-slate-400">Could not determine a Point of No Return for this event</p>
              <p className="text-xs text-slate-500 mt-1">The event may have resolved too quickly for counterfactual analysis</p>
            </div>
          )}
        </>
      )}
    </div>
  );
}

function AutopsyCard({ icon: Icon, value, label, sub, color }: any) {
  return (
    <div className="card text-center">
      <Icon size={20} className="mx-auto mb-2" style={{ color }} />
      <p className="text-xl font-bold text-slate-100">{value}</p>
      <p className="text-xs text-slate-400 mt-1">{label}</p>
      {sub && <p className="text-[10px] text-slate-500 mt-0.5">{sub}</p>}
    </div>
  );
}

function TimelineDot({ time, label, color, last }: { time: string; label: string; color: string; last?: boolean }) {
  return (
    <div className="flex items-start gap-3">
      <div className="flex flex-col items-center">
        <div className="w-3 h-3 rounded-full shrink-0" style={{ background: color }} />
        {!last && <div className="w-0.5 flex-1 min-h-[24px]" style={{ background: '#334155' }} />}
      </div>
      <div>
        <p className="text-sm font-medium text-slate-200">{time}</p>
        <p className="text-xs text-slate-400">{label}</p>
      </div>
    </div>
  );
}
