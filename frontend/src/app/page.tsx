'use client';

import { useEffect, useState } from 'react';
import { api } from '@/lib/api';
import type { DashboardStats } from '@/types';
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  PieChart, Pie, Cell, LineChart, Line, Area, AreaChart
} from 'recharts';
import {
  Activity, AlertTriangle, MapPin, TrendingUp, Zap, Clock
} from 'lucide-react';

const IMPACT_COLORS = ['#22c55e', '#eab308', '#f97316', '#ef4444'];

export default function Dashboard() {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.getDashboardStats().then(setStats).catch(console.error).finally(() => setLoading(false));
  }, []);

  if (loading) return <LoadingSkeleton />;
  if (!stats) return <ErrorState />;

  const typeData = Object.entries(stats.event_type_distribution).map(([k, v]) => ({ name: k, value: v }));
  const impactData = Object.entries(stats.impact_distribution).map(([k, v]) => ({
    name: ['Low', 'Medium', 'High', 'Critical'][Number(k)] || k, value: v
  }));
  const causeData = Object.entries(stats.cause_distribution).map(([k, v]) => ({ name: k, value: v }));
  const corridorData = Object.entries(stats.corridor_distribution).map(([k, v]) => ({ name: k, value: v }));
  const tsData = Object.entries(stats.time_series).slice(-30).map(([k, v]) => ({ date: k.slice(5, 10), count: v }));

  return (
    <div className="space-y-6 animate-fade-in">
      <div>
        <h1 className="text-2xl font-bold text-slate-100">Operational Dashboard</h1>
        <p className="text-slate-400 mt-1">Real-time overview of traffic event intelligence</p>
      </div>

      {/* Metric Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <MetricCard icon={Activity} value={stats.total_events.toLocaleString()} label="Total Events" color="blue" />
        <MetricCard icon={Zap} value={stats.active_events} label="Active Events" color="amber" delta={`${(stats.active_events / stats.total_events * 100).toFixed(1)}%`} />
        <MetricCard icon={AlertTriangle} value={stats.high_impact_events} label="High / Critical Impact" color="red" delta={`${(stats.high_impact_events / stats.total_events * 100).toFixed(1)}%`} />
        <MetricCard icon={MapPin} value={stats.top_junction} label="Most Vulnerable" color="purple" delta={stats.junctions_count + ' junctions'} />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Event Type */}
        <div className="card">
          <h3 className="text-sm font-semibold text-slate-300 mb-4">Event Type Distribution</h3>
          <ResponsiveContainer width="100%" height={280}>
            <PieChart>
              <Pie data={typeData} cx="50%" cy="50%" innerRadius={70} outerRadius={110}
                paddingAngle={4} dataKey="value" stroke="none">
                {typeData.map((_, i) => (
                  <Cell key={i} fill={['#3b82f6', '#f97316'][i]} />
                ))}
              </Pie>
              <Tooltip contentStyle={{ background: '#1e293b', border: '1px solid #334155', borderRadius: 8, color: '#f1f5f9' }} />
            </PieChart>
          </ResponsiveContainer>
          <div className="flex justify-center gap-6 mt-2">
            {typeData.map((d, i) => (
              <div key={d.name} className="flex items-center gap-2">
                <div className="w-3 h-3 rounded-full" style={{ background: ['#3b82f6', '#f97316'][i] }} />
                <span className="text-xs text-slate-400 capitalize">{d.name} ({d.value})</span>
              </div>
            ))}
          </div>
        </div>

        {/* Impact Level */}
        <div className="card">
          <h3 className="text-sm font-semibold text-slate-300 mb-4">Impact Level Distribution</h3>
          <ResponsiveContainer width="100%" height={280}>
            <BarChart data={impactData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
              <XAxis dataKey="name" tick={{ fill: '#94a3b8', fontSize: 12 }} />
              <YAxis tick={{ fill: '#94a3b8', fontSize: 12 }} />
              <Tooltip contentStyle={{ background: '#1e293b', border: '1px solid #334155', borderRadius: 8, color: '#f1f5f9' }} />
              <Bar dataKey="value" radius={[6, 6, 0, 0]} stroke="none">
                {impactData.map((_, i) => (
                  <Cell key={i} fill={IMPACT_COLORS[i % 4]} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Top Causes */}
        <div className="card">
          <h3 className="text-sm font-semibold text-slate-300 mb-4">Top Event Causes</h3>
          <div className="space-y-2">
            {causeData.slice(0, 7).reverse().map((d) => {
              const maxVal = causeData[0]?.value || 1;
              const pct = (d.value / maxVal) * 100;
              return (
                <div key={d.name} className="flex items-center gap-3">
                  <span className="text-xs text-slate-400 w-28 truncate text-right capitalize">{d.name.replace(/_/g, ' ')}</span>
                  <div className="flex-1 h-2.5 bg-surface-lighter rounded-full overflow-hidden">
                    <div className="h-full rounded-full bg-gradient-to-r from-primary-500 to-primary-400 transition-all duration-500"
                      style={{ width: `${pct}%` }} />
                  </div>
                  <span className="text-xs font-medium text-slate-400 w-10 text-right">{d.value}</span>
                </div>
              );
            })}
          </div>
        </div>

        {/* Time Series */}
        <div className="card">
          <h3 className="text-sm font-semibold text-slate-300 mb-4">Events Over Time</h3>
          <ResponsiveContainer width="100%" height={280}>
            <AreaChart data={tsData}>
              <defs>
                <linearGradient id="colorCount" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.3} />
                  <stop offset="95%" stopColor="#3b82f6" stopOpacity={0} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
              <XAxis dataKey="date" tick={{ fill: '#94a3b8', fontSize: 10 }} />
              <YAxis tick={{ fill: '#94a3b8', fontSize: 12 }} />
              <Tooltip contentStyle={{ background: '#1e293b', border: '1px solid #334155', borderRadius: 8, color: '#f1f5f9' }} />
              <Area type="monotone" dataKey="count" stroke="#3b82f6" strokeWidth={2} fill="url(#colorCount)" />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Model Performance */}
      {stats.metrics && (stats.metrics.impact_accuracy || stats.metrics.cascade_accuracy) && (
        <div className="card">
          <h3 className="text-sm font-semibold text-slate-300 mb-4">Model Performance</h3>
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <MetricBadge label="Impact Classifier Accuracy" value={`${((stats.metrics.impact_accuracy || 0) * 100).toFixed(1)}%`} color="blue" />
            <MetricBadge label="Cascade Classifier Accuracy" value={`${((stats.metrics.cascade_accuracy || 0) * 100).toFixed(1)}%`} color="green" />
            <MetricBadge label="Resolution MAE" value={`${(stats.metrics.resolution_mae || 0).toFixed(0)} min`} color="amber" />
          </div>
        </div>
      )}
    </div>
  );
}

function MetricCard({ icon: Icon, value, label, delta, color }: any) {
  const colors: Record<string, string> = {
    blue: 'from-blue-500/20 to-blue-600/10 border-blue-500/30',
    amber: 'from-amber-500/20 to-amber-600/10 border-amber-500/30',
    red: 'from-red-500/20 to-red-600/10 border-red-500/30',
    purple: 'from-purple-500/20 to-purple-600/10 border-purple-500/30',
  };
  return (
    <div className={`card bg-gradient-to-br ${colors[color] || colors.blue}`}>
      <div className="flex items-start justify-between">
        <Icon size={22} className="text-slate-400" />
      </div>
      <p className="metric-value mt-3 text-slate-100 truncate">{value}</p>
      <p className="metric-label mt-1">{label}</p>
      {delta && <p className="text-xs text-slate-500 mt-1">{delta}</p>}
    </div>
  );
}

function MetricBadge({ label, value, color }: { label: string; value: string; color: string }) {
  const colors: Record<string, string> = { blue: 'text-blue-400', green: 'text-emerald-400', amber: 'text-amber-400' };
  return (
    <div className="bg-surface-lighter rounded-lg p-4 text-center">
      <p className={`text-2xl font-bold ${colors[color]}`}>{value}</p>
      <p className="text-xs text-slate-400 mt-1">{label}</p>
    </div>
  );
}

function LoadingSkeleton() {
  return (
    <div className="space-y-6 animate-pulse">
      <div className="h-8 w-64 bg-surface-lighter rounded-lg" />
      <div className="grid grid-cols-4 gap-4">
        {[1, 2, 3, 4].map(i => <div key={i} className="h-28 bg-surface-lighter rounded-xl" />)}
      </div>
      <div className="grid grid-cols-2 gap-6">
        {[1, 2].map(i => <div key={i} className="h-80 bg-surface-lighter rounded-xl" />)}
      </div>
    </div>
  );
}

function ErrorState() {
  return (
    <div className="flex flex-col items-center justify-center h-96 text-slate-400">
      <AlertTriangle size={48} className="mb-4" />
      <p className="text-lg font-medium">Failed to load dashboard</p>
      <p className="text-sm mt-1">Make sure the API server is running on port 8000</p>
    </div>
  );
}
