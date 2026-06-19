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

const IMPACT_COLORS_CHART = ['#059669', '#D97706', '#EA580C', '#DC2626'];
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
    <div className="space-y-7 animate-fade-in">
      <div className="page-header">
        <h1 className="page-title">Event Impact Prediction</h1>
        <p className="page-desc">Forecast impact level, resolution time, and cascade risk</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-5 gap-6">
        {/* Form */}
        <div className="lg:col-span-2 card">
          <h3 className="text-sm font-semibold mb-4 flex items-center gap-2">
            <Radar size={16} className="text-primary-500" /> Event Parameters
          </h3>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              <div>
                <label className="input-label">Event Type</label>
                <select className="select-field" value={form.event_type} onChange={e => update('event_type', e.target.value)}>
                  <option value="unplanned">Unplanned</option>
                  <option value="planned">Planned</option>
                </select>
              </div>
              <div>
                <label className="input-label">Priority</label>
                <select className="select-field" value={form.priority} onChange={e => update('priority', e.target.value)}>
                  <option value="Low">Low</option>
                  <option value="High">High</option>
                </select>
              </div>
            </div>
            <div>
              <label className="input-label">Event Cause</label>
              <select className="select-field" value={form.event_cause} onChange={e => update('event_cause', e.target.value)}>
                {EVENT_CAUSES.map(c => <option key={c} value={c}>{c.replace(/_/g, ' ')}</option>)}
              </select>
            </div>
            <div>
              <label className="input-label">Corridor</label>
              <select className="select-field" value={form.corridor} onChange={e => update('corridor', e.target.value)}>
                {CORRIDORS.map(c => <option key={c} value={c}>{c}</option>)}
              </select>
            </div>
            <div>
              <label className="input-label">Zone</label>
              <select className="select-field" value={form.zone} onChange={e => update('zone', e.target.value)}>
                {ZONES.map(z => <option key={z} value={z}>{z}</option>)}
              </select>
            </div>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              <div>
                <label className="input-label">Hour: {form.hour}:00</label>
                <input type="range" min={0} max={23} value={form.hour}
                  onChange={e => update('hour', Number(e.target.value))}
                  className="range-input" />
              </div>
              <div className="flex items-end pb-2">
                <label className="flex items-center gap-2 cursor-pointer">
                  <input type="checkbox" checked={form.requires_road_closure}
                    onChange={e => update('requires_road_closure', e.target.checked)}
                    className="rounded border-surface-border text-primary-500 focus:ring-primary-200" />
                  <span className="text-xs text-ink-secondary">Road Closure</span>
                </label>
              </div>
            </div>
            <button type="submit" disabled={loading} className="btn-primary w-full mt-2">
              {loading ? 'Analyzing...' : 'Predict Impact'}
            </button>
          </form>
        </div>

        {/* Results */}
        <div className="lg:col-span-3 space-y-4">
          {!result && !loading && (
            <div className="card h-full flex flex-col items-center justify-center min-h-[400px]">
              <Radar size={48} className="mb-4 text-ink-muted/40" />
              <p className="text-sm text-ink-muted">Fill in the event parameters and click Predict</p>
            </div>
          )}
          {loading && (
            <div className="card h-full flex flex-col items-center justify-center min-h-[400px]">
              <div className="w-8 h-8 border-2 border-primary-500 border-t-transparent rounded-full animate-spin" />
              <p className="text-sm text-ink-secondary mt-4">Analyzing event...</p>
            </div>
          )}
          {result && (
            <>
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
                <ResultCard icon={Shield} value={result.impact_label} label="Impact Level"
                  color={['#059669', '#D97706', '#EA580C', '#DC2626'][result.impact_level]} />
                <ResultCard icon={Clock} value={`${result.resolution_minutes} min`} label="Resolution Time" color="#E85D2A" />
                <ResultCard icon={AlertTriangle} value={result.cascade_label} label="Cascade Risk"
                  color={result.cascade_prediction === 1 ? '#DC2626' : '#059669'}
                  delta={`${result.cascade_probability}%`} />
                <ResultCard icon={Radar} value={`${result.confidence}%`} label="Confidence" color="#7C3AED" />
              </div>

              <div className="card">
                <h3 className="text-sm font-semibold mb-3">Resource Recommendation</h3>
                <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
                  <MiniCard icon={Users} value={result.resources.officers} label="Officers" />
                  <MiniCard icon={Cone} value={result.resources.barricades} label="Barricades" />
                  <MiniCard icon={Radio} value={result.resources.monitoring} label="Monitoring" />
                  <MiniCard icon={ArrowLeftRight} value={result.resources.diversion} label="Diversion" />
                </div>
                <p className="text-xs text-ink-muted mt-3">{result.resources.description}</p>
              </div>

              <div className="card">
                <h3 className="text-sm font-semibold mb-4">Impact Probability Distribution</h3>
                <ResponsiveContainer width="100%" height={200}>
                  <BarChart data={result.impact_probabilities.map((p, i) => ({ name: IMPACT_LABELS[i], probability: +(p * 100).toFixed(1) }))}>
                    <XAxis dataKey="name" tick={{ fill: '#A8A29E', fontSize: 12 }} axisLine={false} tickLine={false} />
                    <YAxis domain={[0, 100]} tick={{ fill: '#A8A29E', fontSize: 12 }} axisLine={false} tickLine={false} unit="%" />
                    <Tooltip
                      contentStyle={{ background: '#fff', border: '1px solid #E7E2DC', borderRadius: 10, color: '#1C1917', boxShadow: '0 4px 14px rgba(28,25,23,0.08)' }}
                    />
                    <Bar dataKey="probability" radius={[8, 8, 0, 0]} stroke="none" maxBarSize={48}>
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
      <div className="w-9 h-9 rounded-xl bg-surface-subtle flex items-center justify-center mx-auto mb-2.5" style={{ color }}>
        <Icon size={18} />
      </div>
      <p className="text-lg font-bold" style={{ color }}>{value}</p>
      <p className="metric-label mt-0.5">{label}</p>
      {delta && <p className="text-[10px] text-ink-muted mt-0.5">{delta}</p>}
    </div>
  );
}

function MiniCard({ icon: Icon, value, label }: any) {
  return (
    <div className="bg-surface-subtle rounded-xl p-3.5 text-center border border-surface-border/40">
      <Icon size={16} className="mx-auto mb-1.5 text-ink-muted" />
      <p className="text-sm font-semibold text-ink">{value}</p>
      <p className="text-[10px] text-ink-muted">{label}</p>
    </div>
  );
}
