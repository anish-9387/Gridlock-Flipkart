'use client';

import { useState } from 'react';
import { api } from '@/lib/api';
import type { PredictionInput, PredictionResult } from '@/types';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from 'recharts';
import { Radar, Shield, Clock, AlertTriangle, Users, Cone, Radio, ArrowLeftRight } from 'lucide-react';

const EVENT_CAUSES = [
  'vehicle_breakdown', 'water_logging', 'tree_fall', 'accident', 'construction',
  'public_event', 'procession', 'vip_movement', 'protest', 'pot_holes', 'congestion', 'road_conditions', 'others'
];

const CORRIDORS = [
  'Non-corridor', 'Mysore Road', 'Bellary Road 1', 'Tumkur Road', 'ORR East 1',
  'ORR North 1', 'Hosur Road', 'Magadi Road', 'Old Madras Road', 'Bannerghata Road',
  'ORR East 2', 'ORR North 2', 'West of Chord Road', 'ORR West 1', 'CBD 2',
  'Hennur Main Road', 'Bellary Road 2', 'Varthur Road', 'Old Airport Road', 'IRR(Thanisandra road)'
];

const ZONES = [
  'Central Zone 2', 'West Zone 1', 'North Zone 2', 'West Zone 2', 'South Zone 2',
  'North Zone 1', 'Central Zone 1', 'East Zone 1', 'South Zone 1', 'East Zone 2'
];

const IMPACT_COLORS_CHART = ['#22c55e', '#eab308', '#f97316', '#ef4444'];
const IMPACT_LABELS = ['Low', 'Medium', 'High', 'Critical'];

export default function PredictPage() {
  const [form, setForm] = useState<PredictionInput>({
    event_type: 'unplanned', event_cause: 'vehicle_breakdown', priority: 'Low',
    requires_road_closure: false, corridor: 'Non-corridor', zone: 'Central Zone 2',
    junction: 'unknown', hour: 14,
  });
  const [result, setResult] = useState<PredictionResult | null>(null);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      const r = await api.predict(form);
      setResult(r);
    } catch (err) {
      console.error(err);
    }
    setLoading(false);
  };

  const update = (key: keyof PredictionInput, value: any) => setForm(prev => ({ ...prev, [key]: value }));

  return (
    <div className="space-y-6 animate-fade-in">
      <div>
        <h1 className="text-2xl font-bold text-slate-100">Event Impact Prediction</h1>
        <p className="text-slate-400 mt-1">Forecast impact level, resolution time, and cascade risk</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-5 gap-6">
        {/* Form */}
        <div className="lg:col-span-2 card">
          <h3 className="text-sm font-semibold text-slate-300 mb-4 flex items-center gap-2">
            <Radar size={16} /> Event Parameters
          </h3>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="text-xs font-medium text-slate-400 mb-1.5 block">Event Type</label>
                <select className="select-field" value={form.event_type} onChange={e => update('event_type', e.target.value)}>
                  <option value="unplanned">Unplanned</option>
                  <option value="planned">Planned</option>
                </select>
              </div>
              <div>
                <label className="text-xs font-medium text-slate-400 mb-1.5 block">Priority</label>
                <select className="select-field" value={form.priority} onChange={e => update('priority', e.target.value)}>
                  <option value="Low">Low</option>
                  <option value="High">High</option>
                </select>
              </div>
            </div>
            <div>
              <label className="text-xs font-medium text-slate-400 mb-1.5 block">Event Cause</label>
              <select className="select-field" value={form.event_cause} onChange={e => update('event_cause', e.target.value)}>
                {EVENT_CAUSES.map(c => <option key={c} value={c}>{c.replace(/_/g, ' ')}</option>)}
              </select>
            </div>
            <div>
              <label className="text-xs font-medium text-slate-400 mb-1.5 block">Corridor</label>
              <select className="select-field" value={form.corridor} onChange={e => update('corridor', e.target.value)}>
                {CORRIDORS.map(c => <option key={c} value={c}>{c}</option>)}
              </select>
            </div>
            <div>
              <label className="text-xs font-medium text-slate-400 mb-1.5 block">Zone</label>
              <select className="select-field" value={form.zone} onChange={e => update('zone', e.target.value)}>
                {ZONES.map(z => <option key={z} value={z}>{z}</option>)}
              </select>
            </div>
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="text-xs font-medium text-slate-400 mb-1.5 block">Hour</label>
                <input type="range" min={0} max={23} value={form.hour}
                  onChange={e => update('hour', Number(e.target.value))}
                  className="w-full accent-primary-500" />
                <span className="text-xs text-slate-500">{form.hour}:00</span>
              </div>
              <div className="flex items-end pb-2">
                <label className="flex items-center gap-2 cursor-pointer">
                  <input type="checkbox" checked={form.requires_road_closure}
                    onChange={e => update('requires_road_closure', e.target.checked)}
                    className="rounded border-surface-border bg-surface-light accent-primary-500" />
                  <span className="text-xs text-slate-400">Road Closure</span>
                </label>
              </div>
            </div>
            <button type="submit" disabled={loading} className="btn-primary w-full justify-center mt-2">
              {loading ? 'Analyzing...' : 'Predict Impact'}
            </button>
          </form>
        </div>

        {/* Results */}
        <div className="lg:col-span-3 space-y-4">
          {!result && !loading && (
            <div className="card h-full flex flex-col items-center justify-center text-slate-500 min-h-[400px]">
              <Radar size={48} className="mb-4 opacity-30" />
              <p className="text-sm">Fill in the event parameters and click Predict</p>
            </div>
          )}
          {loading && (
            <div className="card h-full flex flex-col items-center justify-center min-h-[400px]">
              <div className="w-8 h-8 border-2 border-primary-500 border-t-transparent rounded-full animate-spin" />
              <p className="text-sm text-slate-400 mt-4">Analyzing event...</p>
            </div>
          )}
          {result && (
            <>
              {/* Impact & Cascade */}
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
                <ResultCard icon={Shield} value={result.impact_label} label="Impact Level"
                  color={['#22c55e', '#eab308', '#f97316', '#ef4444'][result.impact_level]} />
                <ResultCard icon={Clock} value={`${result.resolution_minutes} min`} label="Resolution Time" color="#3b82f6" />
                <ResultCard icon={AlertTriangle} value={result.cascade_label} label="Cascade Risk"
                  color={result.cascade_prediction === 1 ? '#ef4444' : '#22c55e'}
                  delta={`${result.cascade_probability}%`} />
                <ResultCard icon={Radar} value={`${result.confidence}%`} label="Confidence" color="#8b5cf6" />
              </div>

              {/* Resources */}
              <div className="card">
                <h3 className="text-sm font-semibold text-slate-300 mb-3">Resource Recommendation</h3>
                <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
                  <MiniCard icon={Users} value={result.resources.officers} label="Officers" />
                  <MiniCard icon={Cone} value={result.resources.barricades} label="Barricades" />
                  <MiniCard icon={Radio} value={result.resources.monitoring} label="Monitoring" />
                  <MiniCard icon={ArrowLeftRight} value={result.resources.diversion} label="Diversion" />
                </div>
                <p className="text-xs text-slate-500 mt-3">{result.resources.description}</p>
              </div>

              {/* Probability Chart */}
              <div className="card">
                <h3 className="text-sm font-semibold text-slate-300 mb-4">Impact Probability Distribution</h3>
                <ResponsiveContainer width="100%" height={200}>
                  <BarChart data={result.impact_probabilities.map((p, i) => ({ name: IMPACT_LABELS[i], probability: +(p * 100).toFixed(1) }))}>
                    <XAxis dataKey="name" tick={{ fill: '#94a3b8', fontSize: 12 }} />
                    <YAxis domain={[0, 100]} tick={{ fill: '#94a3b8', fontSize: 12 }} unit="%" />
                    <Tooltip contentStyle={{ background: '#1e293b', border: '1px solid #334155', borderRadius: 8, color: '#f1f5f9' }} />
                    <Bar dataKey="probability" radius={[6, 6, 0, 0]} stroke="none">
                      {result.impact_probabilities.map((_, i) => (
                        <Cell key={i} fill={IMPACT_COLORS_CHART[i]} />
                      ))}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
}

function ResultCard({ icon: Icon, value, label, color, delta }: any) {
  return (
    <div className="card text-center">
      <Icon size={20} className="mx-auto mb-2" style={{ color }} />
      <p className="text-lg font-bold text-slate-100" style={{ color }}>{value}</p>
      <p className="text-xs text-slate-400 mt-0.5">{label}</p>
      {delta && <p className="text-[10px] text-slate-500 mt-0.5">{delta}</p>}
    </div>
  );
}

function MiniCard({ icon: Icon, value, label }: any) {
  return (
    <div className="bg-surface-lighter rounded-lg p-3 text-center">
      <Icon size={16} className="mx-auto mb-1 text-slate-400" />
      <p className="text-sm font-semibold text-slate-100">{value}</p>
      <p className="text-[10px] text-slate-500">{label}</p>
    </div>
  );
}
