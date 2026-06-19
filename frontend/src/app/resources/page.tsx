'use client';

import { useState } from 'react';
import { api } from '@/lib/api';
import type { ResourceResponse } from '@/types';
import { ClipboardList, Users, Cone, Radio, ArrowLeftRight, BarChart3 } from 'lucide-react';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid, Legend } from 'recharts';

export default function ResourcesPage() {
  const [form, setForm] = useState({
    event_cause: 'vehicle_breakdown', priority: 'Low',
    corridor: 'Non-corridor', hour: 14, requires_road_closure: false,
  });
  const [result, setResult] = useState<ResourceResponse | null>(null);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      const r = await api.getResources(form);
      setResult(r);
    } catch (err) {
      console.error(err);
    }
    setLoading(false);
  };

  return (
    <div className="space-y-6 animate-fade-in">
      <div>
        <h1 className="text-2xl font-bold text-slate-100">Resource Planning</h1>
        <p className="text-slate-400 mt-1">Get data-driven resource recommendations for event management</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Form */}
        <div className="lg:col-span-1 card">
          <h3 className="text-sm font-semibold text-slate-300 mb-4 flex items-center gap-2">
            <ClipboardList size={16} /> Event Details
          </h3>
          <form onSubmit={handleSubmit} className="space-y-3.5">
            <div>
              <label className="text-xs font-medium text-slate-400 mb-1 block">Event Cause</label>
              <select className="select-field" value={form.event_cause}
                onChange={e => setForm(p => ({ ...p, event_cause: e.target.value }))}>
                {['vehicle_breakdown', 'water_logging', 'tree_fall', 'accident', 'construction',
                  'public_event', 'procession', 'vip_movement', 'protest', 'pot_holes',
                  'congestion', 'road_conditions', 'others'].map(c => (
                  <option key={c} value={c}>{c.replace(/_/g, ' ')}</option>
                ))}
              </select>
            </div>
            <div>
              <label className="text-xs font-medium text-slate-400 mb-1 block">Priority</label>
              <select className="select-field" value={form.priority}
                onChange={e => setForm(p => ({ ...p, priority: e.target.value }))}>
                <option value="Low">Low</option>
                <option value="High">High</option>
              </select>
            </div>
            <div>
              <label className="text-xs font-medium text-slate-400 mb-1 block">Corridor</label>
              <select className="select-field" value={form.corridor}
                onChange={e => setForm(p => ({ ...p, corridor: e.target.value }))}>
                {['Non-corridor', 'Mysore Road', 'Bellary Road 1', 'Tumkur Road', 'ORR East 1',
                  'ORR North 1', 'Hosur Road', 'Magadi Road', 'Old Madras Road', 'Bannerghata Road',
                  'ORR East 2', 'ORR North 2', 'West of Chord Road', 'ORR West 1', 'CBD 2',
                  'Hennur Main Road', 'Bellary Road 2', 'Varthur Road', 'Old Airport Road',
                  'IRR(Thanisandra road)', 'Airport New South Road', 'CBD 1'].map(c => (
                  <option key={c} value={c}>{c}</option>
                ))}
              </select>
            </div>
            <div>
              <label className="text-xs font-medium text-slate-400 mb-1 block">Hour: {form.hour}:00</label>
              <input type="range" min={0} max={23} value={form.hour}
                onChange={e => setForm(p => ({ ...p, hour: Number(e.target.value) }))}
                className="w-full accent-primary-500" />
            </div>
            <label className="flex items-center gap-2 cursor-pointer">
              <input type="checkbox" checked={form.requires_road_closure}
                onChange={e => setForm(p => ({ ...p, requires_road_closure: e.target.checked }))}
                className="rounded border-surface-border bg-surface-light accent-primary-500" />
              <span className="text-xs text-slate-400">Requires Road Closure</span>
            </label>
            <button type="submit" disabled={loading} className="btn-primary w-full justify-center mt-2">
              {loading ? 'Computing...' : 'Get Recommendations'}
            </button>
          </form>
        </div>

        {/* Results */}
        <div className="lg:col-span-2 space-y-4">
          {!result && !loading && (
            <div className="card h-full flex flex-col items-center justify-center text-slate-500 min-h-[350px]">
              <ClipboardList size={48} className="mb-4 opacity-30" />
              <p className="text-sm">Fill in the event details and click Get Recommendations</p>
            </div>
          )}
          {loading && (
            <div className="card h-full flex flex-col items-center justify-center min-h-[350px]">
              <div className="w-8 h-8 border-2 border-primary-500 border-t-transparent rounded-full animate-spin" />
            </div>
          )}
          {result && (
            <>
              <div className="card">
                <div className="flex items-center gap-2 mb-4">
                  <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium
                    ${result.impact_label === 'Critical' ? 'bg-red-500/15 text-red-400' :
                      result.impact_label === 'High' ? 'bg-orange-500/15 text-orange-400' :
                      result.impact_label === 'Medium' ? 'bg-yellow-500/15 text-yellow-400' :
                      'bg-emerald-500/15 text-emerald-400'}`}>
                    {result.impact_label}
                  </span>
                  <span className="text-xs text-slate-400">Impact Level</span>
                </div>
                <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
                  <ResourceBox icon={Users} value={result.resources.officers} label="Officers" color="#3b82f6" />
                  <ResourceBox icon={Cone} value={result.resources.barricades} label="Barricades" color="#f97316" />
                  <ResourceBox icon={Radio} value={result.resources.monitoring} label="Monitoring" color="#8b5cf6" />
                  <ResourceBox icon={ArrowLeftRight} value={result.resources.diversion} label="Diversion" color="#22c55e" />
                </div>
                <p className="text-xs text-slate-500 mt-4">{result.resources.description}</p>
              </div>

              {/* Reference chart */}
              <div className="card">
                <h3 className="text-sm font-semibold text-slate-300 mb-4 flex items-center gap-2">
                  <BarChart3 size={16} /> Resource Allocation Reference
                </h3>
                <ResponsiveContainer width="100%" height={280}>
                  <BarChart data={result.reference_table}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                    <XAxis dataKey="impact" tick={{ fill: '#94a3b8', fontSize: 12 }} />
                    <YAxis tick={{ fill: '#94a3b8', fontSize: 12 }} />
                    <Tooltip contentStyle={{ background: '#1e293b', border: '1px solid #334155', borderRadius: 8, color: '#f1f5f9' }} />
                    <Legend wrapperStyle={{ fontSize: 12, color: '#94a3b8' }} />
                    <Bar dataKey="officers" name="Officers" fill="#3b82f6" radius={[4, 4, 0, 0]} />
                    <Bar dataKey="barricades" name="Barricades" fill="#f97316" radius={[4, 4, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </div>

              {/* Table */}
              <div className="card overflow-hidden !p-0">
                <div className="overflow-x-auto">
                  <table className="w-full text-sm">
                    <thead>
                      <tr className="border-b border-surface-border">
                        <th className="text-left px-5 py-3 text-xs font-semibold text-slate-400 uppercase">Impact</th>
                        <th className="text-center px-5 py-3 text-xs font-semibold text-slate-400 uppercase">Officers</th>
                        <th className="text-center px-5 py-3 text-xs font-semibold text-slate-400 uppercase">Barricades</th>
                        <th className="text-center px-5 py-3 text-xs font-semibold text-slate-400 uppercase">Monitoring</th>
                        <th className="text-center px-5 py-3 text-xs font-semibold text-slate-400 uppercase">Diversion</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-surface-border/50">
                      {result.reference_table.map((r, i) => (
                        <tr key={r.impact} className={i % 2 === 0 ? 'bg-surface-lighter/20' : ''}>
                          <td className="px-5 py-3 font-medium text-slate-200">{r.impact}</td>
                          <td className="px-5 py-3 text-center text-slate-300">{r.officers}</td>
                          <td className="px-5 py-3 text-center text-slate-300">{r.barricades}</td>
                          <td className="px-5 py-3 text-center text-slate-300">{r.monitoring}</td>
                          <td className="px-5 py-3 text-center text-slate-300">{r.diversion}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>

              <div className="card text-xs text-slate-500 leading-relaxed">
                <p className="font-medium text-slate-400 mb-1">How resources are calculated:</p>
                <ul className="list-disc list-inside space-y-0.5">
                  <li>Base resources determined by impact level (Low → 2 officers, Critical → 15+ officers)</li>
                  <li>Event cause modifiers adjust officer/barricade counts (e.g., public events +30%)</li>
                  <li>Peak hours (8-10 AM, 5-8 PM) increase requirements by 20%</li>
                  <li>Road closure increases barricade needs by 50%</li>
                  <li>Major corridors add 10% to resource requirements</li>
                </ul>
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
}

function ResourceBox({ icon: Icon, value, label, color }: any) {
  return (
    <div className="bg-surface-lighter rounded-lg p-4 text-center">
      <Icon size={18} className="mx-auto mb-1.5" style={{ color }} />
      <p className="text-lg font-bold text-slate-100">{value}</p>
      <p className="text-[10px] text-slate-500 mt-0.5">{label}</p>
    </div>
  );
}
