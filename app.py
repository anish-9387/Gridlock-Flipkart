"""
CascadeIQ — Event Impact Forecasting & Response Intelligence System
Gridlock-Flipkart 2.0 Hackathon · Streamlit dashboard
"""

import os
import sys
import json
import warnings
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import joblib
import streamlit as st
from datetime import timedelta

warnings.filterwarnings('ignore')
st.set_page_config(page_title="CascadeIQ — Event Impact Intelligence", page_icon="🚦",
                   layout="wide", initial_sidebar_state="expanded")
sys.path.insert(0, os.path.dirname(__file__))

from src.feature_engineering import engineer_features, display_resolution, DURATION_BAND_LABELS
from src.models import (load_model, predict_resolution, predict_cascade_proba,
                        explain_prediction, feature_importance)
from src.network import (load_network, simulate_propagation, percolation_early_warning,
                         diversion_candidates, centrality_feature_map)
from src.ttf import estimate_ttf
from src.explain import waterfall_figure, importance_figure, drivers_text, humanize
from src.resources import recommend_resources, IMPACT_RESOURCE_MAP
from src import cascade_autopsy, black_box, early_warning, post_event, digital_twin
from src.similarity import load_similarity_engine, find_similar_events
from src.hotspot_detection import load_hotspot_models
from src.vulnerability import compute_junction_vulnerability, get_fragile_junctions
from src.knowledge_graph import build_event_graph, get_graph_stats

MODELS_DIR = os.path.join(os.path.dirname(__file__), 'models')
DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')
IMPACT_LABELS = {0: 'Low', 1: 'Medium', 2: 'High', 3: 'Critical'}
IMPACT_EMOJI = {0: '🟢 Low', 1: '🟡 Medium', 2: '🟠 High', 3: '🔴 Critical'}
IMPACT_COLORS = {0: '#2ECC71', 1: '#F1C40F', 2: '#E67E22', 3: '#E74C3C'}
CAUSES = ['vehicle_breakdown', 'water_logging', 'tree_fall', 'accident', 'construction',
          'public_event', 'procession', 'vip_movement', 'protest', 'pot_holes',
          'congestion', 'road_conditions', 'others']


@st.cache_resource
def load_artifacts():
    enc = joblib.load(os.path.join(MODELS_DIR, 'encoders.pkl'))
    cal = joblib.load(os.path.join(MODELS_DIR, 'cascade_calibrator.pkl'))
    models = {
        'impact': load_model('impact_classifier'),
        'resolution': load_model('resolution_regressor'),
        'cascade': load_model('cascade_classifier'),
        'prolonged': load_model('prolonged_classifier'),
        'calibrator': cal, 'encoders': enc, 'cmap': enc.get('cmap', {}),
    }
    G, cen = load_network()
    vec, mat, edata = load_similarity_engine()
    hotspots = load_hotspot_models()
    return models, G, cen, (vec, mat, edata), hotspots


@st.cache_data
def load_dataset():
    return pd.read_csv(os.path.join(DATA_DIR, 'dataset.csv'), low_memory=False)


@st.cache_data
def compute_feat(_enc_key):
    df = load_dataset()
    models, *_ = load_artifacts()
    _, t, _, _ = engineer_features(df, is_train=False, encoders=models['encoders'])
    df_feat = df.copy()
    df_feat['resolution_minutes'] = t['resolution_minutes'].to_numpy()
    df_feat['impact_level'] = t['impact_level'].to_numpy()
    df_feat['cascade'] = t['cascade'].to_numpy()
    df_feat['reliable'] = t['reliable'].to_numpy()
    return df_feat


@st.cache_data
def load_metrics():
    p = os.path.join(MODELS_DIR, 'metrics.json')
    return json.load(open(p)) if os.path.exists(p) else {}


@st.cache_data
def load_vuln():
    p = os.path.join(DATA_DIR, 'junction_vulnerability.csv')
    return pd.read_csv(p) if os.path.exists(p) else pd.DataFrame()


def inference_row(p):
    return pd.DataFrame([{
        'event_type': p['event_type'], 'event_cause': p['event_cause'], 'priority': p['priority'],
        'requires_road_closure': p['requires_road_closure'], 'corridor': p['corridor'],
        'zone': p['zone'], 'junction': p.get('junction', 'unknown') or 'unknown',
        'start_datetime': (pd.Timestamp('2024-01-01') + pd.Timedelta(hours=int(p.get('hour', 12)))).strftime('%Y-%m-%d %H:%M:%S'),
        'resolved_datetime': None, 'closed_datetime': None, 'police_station': 'unknown',
        'status': 'active', 'latitude': 12.97, 'longitude': 77.59,
    }])


# ===========================================================================
def main():
    st.title("🚦 CascadeIQ — Event Impact Forecasting & Response Intelligence")
    st.caption("Predicting event escalation before it becomes gridlock · Gridlock-Flipkart 2.0")

    df = load_dataset()
    models, G, cen, (vec, mat, edata), hotspots = load_artifacts()
    df_feat = compute_feat('v2')
    metrics = load_metrics()
    vuln = load_vuln()

    with st.sidebar:
        st.title("CascadeIQ")
        st.caption("Event Impact Intelligence")
        page = st.radio("Navigate", [
            "📊 Dashboard Overview",
            "🔮 Event Impact Prediction",
            "🚨 Early Warning System",
            "🛰️ Network Propagation",
            "🕵️ Cascade Autopsy",
            "🛩️ Traffic Black Box",
            "⚠️ Junction Vulnerability",
            "📍 Hotspot Analysis",
            "🔍 Event Similarity Search",
            "📋 Resource Recommendation",
            "🔄 Digital Twin Simulator",
            "🕸️ Knowledge Graph",
            "📈 Post-Event Learning",
            "🧠 Model Card",
        ])
        st.markdown("---")
        st.caption(f"Dataset: {len(df):,} events · {df['junction'].nunique()} junctions")
        if metrics:
            st.markdown("**Held-out performance**")
            c = metrics.get('cascade', {})
            i = metrics.get('impact', {})
            st.metric("Cascade ROC-AUC", f"{c.get('roc_auc', 0):.3f}")
            st.metric("Cascade Brier ↓", f"{c.get('brier_calibrated', 0):.3f}")
            st.metric("Impact accuracy", f"{i.get('accuracy', 0):.1%}",
                      delta=f"vs {i.get('majority_baseline', 0):.1%} baseline")

    pages = {
        "📊 Dashboard Overview": lambda: page_dashboard(df, df_feat, vuln, metrics, cen),
        "🔮 Event Impact Prediction": lambda: page_prediction(df, models),
        "🚨 Early Warning System": lambda: page_early_warning(df, df_feat, models, G, cen),
        "🛰️ Network Propagation": lambda: page_network(df, models, G, cen),
        "🕵️ Cascade Autopsy": lambda: page_autopsy(df_feat, models, G),
        "🛩️ Traffic Black Box": lambda: page_black_box(df_feat, models),
        "⚠️ Junction Vulnerability": lambda: page_vulnerability(vuln),
        "📍 Hotspot Analysis": lambda: page_hotspots(df, hotspots),
        "🔍 Event Similarity Search": lambda: page_similarity(df, vec, mat, edata),
        "📋 Resource Recommendation": lambda: page_resources(),
        "🔄 Digital Twin Simulator": lambda: page_digital_twin(df, models),
        "🕸️ Knowledge Graph": lambda: page_knowledge_graph(df_feat),
        "📈 Post-Event Learning": lambda: page_post_event(df, df_feat, models),
        "🧠 Model Card": lambda: page_model_card(metrics),
    }
    pages[page]()


# --------------------------------------------------------------------------- dashboard
def page_dashboard(df, df_feat, vuln, metrics, cen):
    st.header("📊 Operational Dashboard")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Events", f"{len(df):,}")
    c2.metric("Active Now", int((df['status'].astype(str).str.lower() == 'active').sum()))
    hi = int((df_feat['impact_level'] >= 2).sum())
    c3.metric("High/Critical Impact", hi, delta=f"{hi/len(df_feat)*100:.0f}%")
    c4.metric("Most Fragile Junction", vuln.iloc[0]['junction'] if len(vuln) else "N/A")

    st.markdown("---")
    a, b = st.columns(2)
    with a:
        st.subheader("Impact Distribution")
        ic = df_feat['impact_level'].value_counts().sort_index()
        fig = px.bar(x=[IMPACT_LABELS[i] for i in ic.index], y=ic.values,
                     color=[IMPACT_LABELS[i] for i in ic.index],
                     color_discrete_map={v: IMPACT_COLORS[k] for k, v in IMPACT_LABELS.items()})
        fig.update_layout(height=320, showlegend=False, xaxis_title="", yaxis_title="Events")
        st.plotly_chart(fig, width='stretch')
    with b:
        st.subheader("Top Event Causes")
        cc = df['event_cause'].value_counts().head(8)
        fig = px.bar(y=cc.index, x=cc.values, orientation='h', color=cc.values,
                     color_continuous_scale='YlOrRd')
        fig.update_layout(height=320, xaxis_title="Events", yaxis_title="",
                          coloraxis_showscale=False)
        st.plotly_chart(fig, width='stretch')

    st.markdown("---")
    st.subheader("📈 Events Over Time")
    dts = pd.to_datetime(df['start_datetime'], utc=True, errors='coerce')
    daily = dts.dt.date.value_counts().sort_index()
    fig = px.area(x=list(daily.index), y=daily.values, labels={'x': 'Date', 'y': 'Events'})
    fig.update_layout(height=300)
    st.plotly_chart(fig, width='stretch')

    st.markdown("---")
    st.subheader("🏆 Most Structurally Fragile Junctions (betweenness-based)")
    if len(vuln):
        cols = [c for c in ['junction', 'risk_score', 'risk_category', 'betweenness_norm',
                            'cascade_rate', 'event_count'] if c in vuln.columns]
        st.dataframe(vuln.head(10)[cols], width='stretch', hide_index=True)


# --------------------------------------------------------------------------- prediction
def page_prediction(df, models):
    st.header("🔮 Event Impact Prediction")
    st.caption("Impact, calibrated cascade risk, Time-To-Failure and the *why* (tree-SHAP).")
    with st.form("predict"):
        c1, c2 = st.columns(2)
        with c1:
            etype = st.selectbox("Event Type", ['unplanned', 'planned'])
            cause = st.selectbox("Event Cause", CAUSES)
            priority = st.selectbox("Priority", ['High', 'Low'])
            closure = st.checkbox("Requires Road Closure")
        with c2:
            corridor = st.selectbox("Corridor", sorted(df['corridor'].dropna().unique()))
            zone = st.selectbox("Zone", sorted(df['zone'].dropna().unique()))
            junction = st.selectbox("Junction", ['unknown'] + sorted(
                [j for j in df['junction'].dropna().unique() if str(j).lower() != 'unknown']))
            hour = st.slider("Hour of Day", 0, 23, 18)
        go_pred = st.form_submit_button("🔮 Predict", type="primary")

    if not go_pred:
        return
    p = dict(event_type=etype, event_cause=cause, priority=priority,
             requires_road_closure=closure, corridor=corridor, zone=zone,
             junction=junction, hour=hour)
    X, _, _, cols = engineer_features(inference_row(p), is_train=False, encoders=models['encoders'])
    impact = int(models['impact'].predict(X)[0])
    proba = models['impact'].predict_proba(X)[0]
    resolution = display_resolution(predict_resolution(models['resolution'], X)[0], cause, models['encoders'])
    cascade_p = float(predict_cascade_proba(models['cascade'], models['calibrator'], X)[0])
    frag = float(models['cmap'].get(junction.lower().replace(' ', ''), {}).get('betweenness_norm', 0.0))
    peak = (8 <= hour <= 10) or (17 <= hour <= 20)
    ttf = estimate_ttf(cascade_p, impact, resolution, frag, peak)

    st.markdown("---")
    m = st.columns(4)
    m[0].metric("Impact", IMPACT_EMOJI[impact], delta=f"{proba.max()*100:.0f}% confidence")
    m[1].metric("Est. Resolution", f"{resolution:.0f} min", help="Historical-anchored estimate")
    m[2].metric("Cascade Risk", f"{cascade_p*100:.0f}%",
                delta="calibrated", delta_color="off")
    m[3].metric("⏱ Time-To-Failure", f"{ttf['time_to_failure_min']:.0f} min",
                delta=ttf['risk_level'], delta_color="inverse")
    st.info(f"**Decision window:** {ttf['headline']}")

    res = recommend_resources(impact, cause, closure, corridor, hour)
    r = st.columns(4)
    r[0].metric("👮 Officers", res['officers'])
    r[1].metric("🚧 Barricades", res['barricades'])
    r[2].metric("📡 Monitoring", res['monitoring'])
    r[3].metric("🔄 Diversion", res['diversion'])

    st.markdown("---")
    a, b = st.columns([1, 1])
    with a:
        st.subheader("Impact Probability")
        pdf = pd.DataFrame({'Impact': [IMPACT_LABELS[i] for i in range(len(proba))],
                            'Probability': proba * 100})
        fig = px.bar(pdf, x='Impact', y='Probability', color='Impact',
                     color_discrete_map={v: IMPACT_COLORS[k] for k, v in IMPACT_LABELS.items()},
                     text_auto='.0f')
        fig.update_layout(height=320, showlegend=False, yaxis_title="%")
        st.plotly_chart(fig, width='stretch')
    with b:
        st.subheader("Why this prediction? (tree-SHAP)")
        expl = explain_prediction(models['impact'], X[0], cols, top_k=7, predicted_class=impact)
        st.plotly_chart(waterfall_figure(expl, ''), width='stretch')

    # log the prediction for the post-event learning loop
    post_event.log_prediction({
        'event_id': f"live-{cause}-{junction}", 'event_cause': cause, 'junction': junction,
        'corridor': corridor, 'predicted_impact': impact, 'predicted_resolution': resolution,
        'predicted_cascade_prob': cascade_p})
    st.caption("✓ Prediction logged to the Post-Event Learning store.")


# --------------------------------------------------------------------------- early warning
def page_early_warning(df, df_feat, models, G, cen):
    st.header("🚨 Early Warning System")
    st.caption("Pre-event risk index + recommended deployment lead time — act *before* the event.")
    with st.form("ew"):
        c1, c2 = st.columns(2)
        with c1:
            etype = st.selectbox("Event Type", ['planned', 'unplanned'])
            cause = st.selectbox("Event Cause", CAUSES, index=5)
            priority = st.selectbox("Priority", ['High', 'Low'])
            closure = st.checkbox("Road Closure", value=True)
        with c2:
            corridor = st.selectbox("Corridor", sorted(df['corridor'].dropna().unique()))
            zone = st.selectbox("Zone", sorted(df['zone'].dropna().unique()))
            junction = st.selectbox("Junction", ['unknown'] + sorted(
                [j for j in df['junction'].dropna().unique() if str(j).lower() != 'unknown']))
            hour = st.slider("Planned Start Hour", 0, 23, 18)
        go_ew = st.form_submit_button("🚨 Assess Risk", type="primary")

    if go_ew:
        p = dict(event_type=etype, event_cause=cause, priority=priority,
                 requires_road_closure=closure, corridor=corridor, zone=zone,
                 junction=junction, hour=hour)
        r = early_warning.assess_event(p, models['impact'], models['resolution'],
                                       models['cascade'], models['calibrator'],
                                       models['encoders'], engineer_features, models['cmap'])
        st.markdown("---")
        col1, col2 = st.columns([1, 2])
        with col1:
            fig = go.Figure(go.Indicator(
                mode="gauge+number", value=r['risk_index'],
                title={'text': r['risk_band']},
                gauge={'axis': {'range': [0, 100]}, 'bar': {'color': r['risk_color']},
                       'steps': [{'range': [0, 20], 'color': '#eafaf1'},
                                 {'range': [20, 40], 'color': '#fef9e7'},
                                 {'range': [40, 66], 'color': '#fdebd0'},
                                 {'range': [66, 100], 'color': '#fadbd8'}]}))
            fig.update_layout(height=300, margin=dict(t=40, b=10))
            st.plotly_chart(fig, width='stretch')
        with col2:
            st.metric("Recommended deployment lead time", f"{r['lead_time_hours']:.0f} hours before start")
            st.metric("⏱ Time-To-Failure (est.)", f"{r['ttf']['time_to_failure_min']:.0f} min")
            st.markdown("**Triggers:**")
            for t in r['triggers']:
                st.markdown(f"- {t}")
        st.success(f"**{r['recommendation']}**")

    st.markdown("---")
    st.subheader("🌐 Live City-Wide Risk (active events)")
    active = df_feat[df_feat['status'].astype(str).str.lower() == 'active'].copy()
    cr = early_warning.city_risk(active.head(40), G, cen)
    if cr.get('active_events'):
        cc = st.columns(3)
        cc[0].metric("Active Events", cr['active_events'])
        cc[1].metric("Sources on network", len(cr.get('source_junctions', [])))
        cc[2].metric("Percolation precursor", f"{cr['precursor_min']:.0f} min"
                     if cr.get('precursor_min') else "—")
        curve = cr.get('percolation_curve')
        if curve is not None and len(curve):
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=curve['time_min'], y=curve['clusters'],
                                     name='Congested clusters', line=dict(color='#E67E22')))
            fig.add_trace(go.Scatter(x=curve['time_min'], y=curve['giant_component'],
                                     name='Giant component', line=dict(color='#E74C3C')))
            if cr.get('precursor_min'):
                fig.add_vline(x=cr['precursor_min'], line_dash='dash',
                              annotation_text='Peak-cluster precursor')
            fig.update_layout(height=320, xaxis_title="minutes", yaxis_title="junctions",
                              title="Percolation: clusters merge into a giant component at collapse")
            st.plotly_chart(fig, width='stretch')


# --------------------------------------------------------------------------- network propagation
def page_network(df, models, G, cen):
    st.header("🛰️ Network Propagation Engine")
    st.caption("Road-network graph of 294 junctions · betweenness fragility · cascade spread.")
    junctions = sorted(cen['junction'].tolist())
    default = cen.iloc[0]['junction']
    src = st.selectbox("Source junction (where disruption starts)", junctions,
                       index=junctions.index(default))
    speed = st.slider("Cascade spread speed (km/h)", 8, 40, 18)

    prop = simulate_propagation(G, src, cen, spread_speed_kmph=speed)
    if prop.empty:
        st.warning("No propagation from this junction.")
        return
    tmax = float(prop['time_to_impact_min'].max())
    t = st.slider("Time since onset (minutes)", 0.0, round(tmax, 1), round(min(20.0, tmax), 1))
    snap = prop[prop['time_to_impact_min'] <= t]

    c1, c2, c3 = st.columns(3)
    c1.metric("Junctions reached", f"{len(snap)} / {len(prop)}")
    c2.metric("At-risk (stressed)", int(snap['at_risk'].sum()))
    stats, crit = percolation_early_warning(G, prop)
    c3.metric("Network-critical at", f"{crit:.0f} min" if crit else "—")

    snap = snap.assign(sz=snap['stress_level'] * 18 + 5)
    fig = px.scatter_mapbox(snap, lat='latitude', lon='longitude', color='stress_level',
                            size='sz', color_continuous_scale='YlOrRd',
                            range_color=[0, 1], zoom=10.5, mapbox_style='carto-positron',
                            hover_name='junction', height=480)
    s = prop[prop['is_source']].iloc[0]
    fig.add_trace(go.Scattermapbox(lat=[s['latitude']], lon=[s['longitude']], mode='markers',
                                   marker=dict(size=20, color='blue'), name='Source'))
    st.plotly_chart(fig, width='stretch')

    a, b = st.columns(2)
    with a:
        st.subheader("Collapse curve")
        if len(stats):
            fig = px.area(stats, x='time_min', y='giant_frac',
                          labels={'giant_frac': 'stressed network fraction', 'time_min': 'minutes'})
            fig.add_hline(y=0.5, line_dash='dash', annotation_text='network-critical (50%)')
            fig.update_layout(height=300)
            st.plotly_chart(fig, width='stretch')
    with b:
        st.subheader("🔀 Diversion candidates")
        st.caption(f"If **{src}** is blocked, route through low-fragility bypasses:")
        div = diversion_candidates(G, cen, src)
        if len(div):
            st.dataframe(div[['junction', 'corridor', 'fragility', 'spare_capacity']],
                         width='stretch', hide_index=True)
        else:
            st.info("No bypass candidates found.")


# --------------------------------------------------------------------------- cascade autopsy
def page_autopsy(df_feat, models, G):
    st.header("🕵️ Cascade Autopsy — Counterfactual Analysis")
    st.caption("Replay a historical event; find the decision window and the preventable share.")
    pool = df_feat[(df_feat['reliable']) & (df_feat['impact_level'] >= 1)].copy()
    pool = pool[pool['junction'].astype(str).str.lower() != 'unknown']
    pool['lbl'] = pool.apply(lambda r: f"[{r['id']}] {r['event_cause']} @ {r['junction']} "
                             f"({r['resolution_minutes']:.0f}min, {IMPACT_LABELS[int(r['impact_level'])]})", axis=1)
    pool = pool.sort_values('impact_level', ascending=False).head(150)
    choice = st.selectbox("Select event", pool['lbl'].tolist())
    if not st.button("🔬 Run Autopsy", type="primary"):
        return
    eid = choice.split(']')[0].strip('[')
    row = pool[pool['id'].astype(str) == eid].iloc[0].to_dict()
    r = cascade_autopsy.run_autopsy(row, models['impact'], models['resolution'], models['cascade'],
                                    models['calibrator'], models['encoders'], engineer_features,
                                    models['cmap'], G)
    base = r['base']
    st.markdown("---")
    c = st.columns(4)
    c[0].metric("Predicted Impact", IMPACT_LABELS[base['impact']])
    c[1].metric("Cascade Prob.", f"{base['cascade_p']*100:.0f}%")
    c[2].metric("⏱ Point of No Return", r['point_of_no_return_time'],
                delta=f"{r['decision_window_min']:.0f} min window")
    c[3].metric("Network-critical", f"{r['network_critical_min']:.0f} min"
                if r['network_critical_min'] else "—")

    st.markdown("---")
    if r['preventable'] and r['best_counterfactual']:
        st.success(f"**Preventable** — {r['best_counterfactual']['lever']} cuts cascade risk by "
                   f"{r['cascade_reduction']*100:.0f}%.")
        cf = r['best_counterfactual']
        a, b = st.columns(2)
        with a:
            st.markdown("#### ❌ Reality")
            st.markdown(f"- Impact: **{IMPACT_LABELS[base['impact']]}**")
            st.markdown(f"- Cascade risk: **{base['cascade_p']*100:.0f}%**")
            st.markdown(f"- TTF: **{base['ttf']['time_to_failure_min']:.0f} min**")
        with b:
            st.markdown(f"#### ✅ Counterfactual — {cf['lever']}")
            st.markdown(f"- Impact: **{IMPACT_LABELS[cf['impact']]}**")
            st.markdown(f"- Cascade risk: **{cf['cascade_p']*100:.0f}%**")
            st.markdown(f"- TTF: **{cf['ttf']['time_to_failure_min']:.0f} min**")
    else:
        st.info("No single lever materially prevents escalation for this event "
                "(low controllable risk, or already minor).")

    if len(r['propagation']):
        st.markdown("---")
        st.subheader("Stress spread from event junction")
        prop_viz = r['propagation'].assign(sz=r['propagation']['stress_level'] * 15 + 4)
        fig = px.scatter_mapbox(prop_viz, lat='latitude', lon='longitude',
                                color='stress_level', color_continuous_scale='YlOrRd',
                                size='sz', zoom=10.5, mapbox_style='carto-positron', height=420)
        st.plotly_chart(fig, width='stretch')


# --------------------------------------------------------------------------- black box
def page_black_box(df_feat, models):
    st.header("🛩️ Traffic Black Box")
    st.caption("Post-event reconstruction · root-cause analysis · avoidable-delay accounting.")
    pool = df_feat[df_feat['reliable']].copy()
    pool = pool[pool['junction'].astype(str).str.lower() != 'unknown']
    pool['lbl'] = pool.apply(lambda r: f"[{r['id']}] {r['event_cause']} @ {r['junction']} "
                             f"({r['resolution_minutes']:.0f}min)", axis=1)
    pool = pool.sort_values('resolution_minutes', ascending=False).head(150)
    choice = st.selectbox("Select resolved event", pool['lbl'].tolist())
    if not st.button("🛩️ Open Black Box", type="primary"):
        return
    eid = choice.split(']')[0].strip('[')
    row = pool[pool['id'].astype(str) == eid].iloc[0].to_dict()

    tl, dur = black_box.reconstruct_timeline(row)
    rca = black_box.root_cause_analysis(row, models['impact'], models['encoders'], engineer_features)
    av = black_box.avoidable_delay(row, df_feat)

    st.markdown("---")
    a, b = st.columns([1, 1])
    with a:
        st.subheader("⏱ Reconstruction")
        for s in tl:
            tt = s['time'].strftime('%H:%M') if s['time'] is not None else '--:--'
            icon = {'start': '🟢', 'escalation': '🟠', 'peak': '🔴', 'end': '✅', 'active': '⏳'}.get(s['type'], '•')
            st.markdown(f"- {icon} **{tt}** — {s['label']}")
    with b:
        st.subheader("🔎 Root Cause")
        st.markdown(f"**Primary:** {rca['primary_cause']}")
        if rca['contributing_factors']:
            st.markdown("**Contributing factors:**")
            for f in rca['contributing_factors']:
                st.markdown(f"- {f}")

    if av:
        st.markdown("---")
        st.subheader("⏳ Avoidable-Delay Analysis")
        c = st.columns(3)
        c[0].metric("Actual resolution", f"{av['actual_minutes']:.0f} min")
        c[1].metric(f"Historical median ({av['cause']})", f"{av['historical_median_minutes']:.0f} min")
        c[2].metric("Avoidable delay", f"{av['avoidable_minutes']:.0f} min",
                    delta=f"{av['avoidable_pct']:.0f}% of total", delta_color="inverse")
        st.caption(f"Compared against {av['peer_count']} comparable historical events.")


# --------------------------------------------------------------------------- vulnerability
def page_vulnerability(vuln):
    st.header("⚠️ Junction Vulnerability (Fragility)")
    st.caption("Fragility = 0.40·betweenness + 0.30·cascade-rate + 0.20·degree + 0.10·peak-incidents")
    if not len(vuln):
        st.warning("Run train.py to compute vulnerability.")
        return
    top_n = st.slider("Show top N", 5, 50, 20)
    show = vuln.head(top_n)
    fig = px.bar(show.head(15), x='junction', y='risk_score', color='risk_category',
                 color_discrete_map={'Low': '#2ECC71', 'Medium': '#F1C40F',
                                     'High': '#E67E22', 'Critical': '#E74C3C'}, text_auto='.1f')
    fig.update_layout(height=420, xaxis_tickangle=-45)
    st.plotly_chart(fig, width='stretch')
    cols = [c for c in ['junction', 'risk_score', 'risk_category', 'betweenness_norm',
                        'cascade_rate', 'degree', 'event_count', 'avg_resolution_minutes']
            if c in vuln.columns]
    st.dataframe(show[cols], width='stretch', hide_index=True)


# --------------------------------------------------------------------------- hotspots
def page_hotspots(df, hotspots):
    st.header("📍 Hotspot Analysis")
    st.caption("DBSCAN spatial clustering of recurring incident zones by cause.")
    opts = list(hotspots.keys()) if hotspots else []
    if not opts:
        st.warning("No hotspots available.")
        return
    cause = st.selectbox("Event cause", opts)
    hdf = hotspots[cause]
    st.dataframe(hdf, width='stretch', hide_index=True)
    sub = df[df['event_cause'].astype(str).str.lower() == str(cause).lower()].dropna(
        subset=['latitude', 'longitude']).head(500)
    fig = px.scatter_mapbox(sub, lat='latitude', lon='longitude', color='priority',
                            zoom=10.5, mapbox_style='carto-positron', height=460)
    for _, h in hdf.iterrows():
        fig.add_trace(go.Scattermapbox(lat=[h['avg_lat']], lon=[h['avg_lon']], mode='markers',
                                       marker=dict(size=h['count'] * 2 + 8, color='red', opacity=0.6),
                                       name=f"{int(h['count'])} events"))
    st.plotly_chart(fig, width='stretch')


# --------------------------------------------------------------------------- similarity
def page_similarity(df, vec, mat, edata):
    st.header("🔍 Event Similarity Search")
    st.caption("TF-IDF vector search over 8,173 historical events.")
    if edata is None:
        st.warning("Similarity engine not trained.")
        return
    with st.form("sim"):
        c1, c2 = st.columns(2)
        with c1:
            cause = st.selectbox("Cause", sorted(df['event_cause'].dropna().unique()))
            priority = st.selectbox("Priority", ['High', 'Low'])
            etype = st.selectbox("Type", ['unplanned', 'planned'])
        with c2:
            corridor = st.selectbox("Corridor", sorted(df['corridor'].dropna().unique()))
            zone = st.selectbox("Zone", sorted(df['zone'].dropna().unique()))
            junction = st.selectbox("Junction", ['unknown'] + sorted(
                [j for j in df['junction'].dropna().unique() if str(j).lower() != 'unknown']))
        go_sim = st.form_submit_button("🔍 Find Similar", type="primary")
    if go_sim:
        q = dict(event_cause=cause, corridor=corridor, zone=zone, junction=junction,
                 event_type=etype, priority=priority, police_station='unknown')
        res = find_similar_events(q, vec, mat, edata, top_k=5)
        for i, r in enumerate(res, 1):
            with st.container():
                a, b = st.columns([3, 1])
                a.markdown(f"**{i}. {r['event_cause']}** @ {r.get('junction', '?')} · "
                           f"{r['corridor']} / {r['zone']} · {r['priority']} priority")
                b.markdown(f"**{r['similarity_score']:.0%}** match")
                a.caption(f"Impact: {IMPACT_LABELS.get(int(r['impact_level']), '?')} · "
                          f"Resolution: {r.get('resolution_minutes', 'N/A')} min")
                st.divider()


# --------------------------------------------------------------------------- resources
def page_resources():
    st.header("📋 Resource Recommendation")
    c1, c2 = st.columns(2)
    with c1:
        cause = st.selectbox("Cause", CAUSES)
        priority = st.selectbox("Priority", ['High', 'Low'])
    with c2:
        corridor = st.text_input("Corridor", "ORR East 1")
        hour = st.slider("Hour", 0, 23, 18)
        closure = st.checkbox("Road closure")
    if st.button("📋 Recommend", type="primary"):
        impact = 2 if priority == 'High' else 0
        if cause in ('public_event', 'procession', 'vip_movement'):
            impact = max(impact, 2)
        if closure:
            impact = min(impact + 1, 3)
        res = recommend_resources(impact, cause, closure, corridor, hour)
        c = st.columns(4)
        c[0].metric("👮 Officers", res['officers'])
        c[1].metric("🚧 Barricades", res['barricades'])
        c[2].metric("📡 Monitoring", res['monitoring'])
        c[3].metric("🔄 Diversion", res['diversion'])
        st.info(res['description'])
        ref = pd.DataFrame([{'Impact': v['impact'], 'Officers': v['officers'],
                             'Barricades': v['barricades'], 'Monitoring': v['monitoring']}
                            for v in IMPACT_RESOURCE_MAP.values()])
        st.dataframe(ref, width='stretch', hide_index=True)


# --------------------------------------------------------------------------- digital twin
def page_digital_twin(df, models):
    st.header("🔄 Traffic Digital Twin Simulator")
    st.caption("Compare scenarios side-by-side: impact, resolution, cascade, TTF, resources.")
    if 'twin_scenarios' not in st.session_state:
        st.session_state.twin_scenarios = []
    with st.expander("➕ Add scenario", expanded=len(st.session_state.twin_scenarios) == 0):
        with st.form("twin"):
            c1, c2 = st.columns(2)
            with c1:
                name = st.text_input("Name", f"Scenario {len(st.session_state.twin_scenarios)+1}")
                etype = st.selectbox("Type", ['unplanned', 'planned'], key='tt')
                cause = st.selectbox("Cause", CAUSES, key='tc')
                priority = st.selectbox("Priority", ['High', 'Low'], key='tp')
            with c2:
                corridor = st.selectbox("Corridor", sorted(df['corridor'].dropna().unique()), key='tco')
                zone = st.selectbox("Zone", sorted(df['zone'].dropna().unique()), key='tz')
                junction = st.selectbox("Junction", ['Unknown'] + sorted(
                    [j for j in df['junction'].dropna().unique() if str(j).lower() != 'unknown']), key='tj')
                hour = st.slider("Hour", 0, 23, 18, key='th')
                closure = st.checkbox("Road closure", key='tcl')
            if st.form_submit_button("➕ Add", type="primary"):
                st.session_state.twin_scenarios.append(dict(
                    name=name, event_type=etype, event_cause=cause, priority=priority,
                    requires_road_closure=closure, corridor=corridor, zone=zone,
                    junction=junction, hour=hour))
                st.rerun()
    if st.session_state.twin_scenarios:
        st.write(f"**{len(st.session_state.twin_scenarios)} scenario(s) queued**")
        cols = st.columns([1, 1])
        if cols[0].button("🔄 Run Comparison", type="primary"):
            res = digital_twin.compare_scenarios(
                st.session_state.twin_scenarios, models['impact'], models['resolution'], models['cascade'],
                models['calibrator'], models['encoders'], models['cmap'])
            st.session_state.twin_res = digital_twin.scenarios_to_dataframe(res)
        if cols[1].button("🗑️ Clear"):
            st.session_state.twin_scenarios = []
            st.session_state.pop('twin_res', None)
            st.rerun()
    if st.session_state.get('twin_res') is not None:
        rdf = st.session_state.twin_res
        st.dataframe(rdf, width='stretch', hide_index=True)
        rdf2 = rdf.copy()
        rdf2['Cascade Prob.'] = pd.to_numeric(rdf2['Cascade Prob.'].str.rstrip('%'), errors='coerce')
        fig = px.bar(rdf2, x='Scenario', y='Cascade Prob.', color='Impact Level',
                     color_discrete_map={v: IMPACT_COLORS[k] for k, v in IMPACT_LABELS.items()},
                     text='Risk')
        fig.update_layout(height=380, yaxis_title="Cascade probability (%)")
        st.plotly_chart(fig, width='stretch')


# --------------------------------------------------------------------------- knowledge graph
def page_knowledge_graph(df_feat):
    st.header("🕸️ Knowledge Graph — Event Relationships")
    c1, c2, c3 = st.columns(3)
    max_nodes = c1.slider("Max events", 20, 100, 50)
    min_sim = c2.slider("Min similarity", 0.05, 0.8, 0.25, 0.05)
    cause = c3.selectbox("Cause", ['All'] + sorted(df_feat['event_cause'].dropna().unique().tolist()))
    nodes, edges = build_event_graph(df_feat, max_nodes=max_nodes, min_similarity=min_sim,
                                     filter_cause=cause)
    if nodes.empty:
        st.warning("Not enough connected events. Lower the similarity threshold.")
        return
    stats = get_graph_stats(nodes, edges)
    cc = st.columns(4)
    cc[0].metric("Nodes", stats['nodes'])
    cc[1].metric("Edges", stats['edges'])
    cc[2].metric("Clusters", stats['clusters'])
    cc[3].metric("Avg degree", stats['avg_degree'])
    ex, ey = [], []
    for _, e in edges.iterrows():
        s = nodes[nodes['id'] == e['source']].iloc[0]
        t = nodes[nodes['id'] == e['target']].iloc[0]
        ex += [s['x'], t['x'], None]
        ey += [s['y'], t['y'], None]
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=ex, y=ey, mode='lines', line=dict(width=0.5, color='#bbb'),
                             hoverinfo='none'))
    fig.add_trace(go.Scatter(x=nodes['x'], y=nodes['y'], mode='markers',
                             marker=dict(size=nodes['degree'].clip(6, 24),
                                         color=[IMPACT_COLORS.get(int(i), '#888') for i in nodes['impact_level']]),
                             text=nodes['event_cause'], hovertemplate="%{text}<extra></extra>"))
    fig.update_layout(height=560, showlegend=False, xaxis_visible=False, yaxis_visible=False)
    st.plotly_chart(fig, width='stretch')


# --------------------------------------------------------------------------- post-event learning
def page_post_event(df, df_feat, models):
    st.header("📈 Post-Event Learning System")
    st.caption("The loop the brief asks for: store predictions, match to outcomes, measure & improve.")
    if st.button("🔁 (Re)build learning evidence from history"):
        with st.spinner("Replaying historical events through the live models..."):
            X, t, _, _ = engineer_features(df, is_train=True, centrality_map=models['cmap'])
            n = post_event.seed_from_history(df, X, t, models['impact'], models['resolution'],
                                             models['cascade'], models['calibrator'], n=500)
        st.success(f"Logged {n} prediction-vs-actual records.")

    s = post_event.learning_summary()
    if not s:
        st.info("No records yet — click the button above to seed from history, or make predictions.")
        return
    c = st.columns(4)
    c[0].metric("Predictions logged", s['total_predictions'])
    c[1].metric("With ground truth", s['with_ground_truth'])
    c[2].metric("Impact accuracy", f"{s.get('impact_accuracy', 0):.1%}",
                delta=f"±1: {s.get('impact_within_1', 0):.0%}")
    c[3].metric("Resolution MedAE", f"{s.get('resolution_medae', 0):.0f} min")

    a, b = st.columns(2)
    with a:
        st.subheader("Cascade calibration (reliability curve)")
        cal = s.get('calibration')
        if cal is not None and len(cal):
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=[0, 1], y=[0, 1], mode='lines',
                                     line=dict(dash='dash', color='gray'), name='perfect'))
            fig.add_trace(go.Scatter(x=cal['predicted'], y=cal['observed'], mode='lines+markers',
                                     name='model', line=dict(color='#3498DB')))
            fig.update_layout(height=320, xaxis_title="predicted probability",
                              yaxis_title="observed rate")
            st.plotly_chart(fig, width='stretch')
            st.caption(f"Brier score: {s.get('cascade_brier', 0):.4f} (lower is better)")
    with b:
        st.subheader("Accuracy over time (drift)")
        ts = post_event.accuracy_over_time(freq='W')
        if len(ts):
            fig = px.line(ts, x='ts', y='accuracy', markers=True)
            fig.update_layout(height=320, yaxis_range=[0, 1])
            st.plotly_chart(fig, width='stretch')


# --------------------------------------------------------------------------- model card
def page_model_card(metrics):
    st.header("🧠 Model Card — Honest Performance & Methodology")
    if not metrics:
        st.warning("Run train.py to generate metrics.")
        return
    st.markdown("All metrics below are on a **chronological held-out test set** "
                "(train Nov→Mar, test Mar→Apr) with encoders fit on train only — no leakage.")
    imp, casc = metrics.get('impact', {}), metrics.get('cascade', {})
    band, res = metrics.get('duration_prolonged', {}), metrics.get('resolution', {})

    c = st.columns(3)
    c[0].metric("Cascade ROC-AUC", f"{casc.get('roc_auc', 0):.3f}",
                help="vs random 0.50; strong discrimination")
    c[0].metric("Cascade PR-AUC", f"{casc.get('pr_auc', 0):.3f}",
                delta=f"base rate {casc.get('positive_rate', 0):.2f}")
    c[1].metric("Cascade Brier (calibrated)", f"{casc.get('brier_calibrated', 0):.4f}",
                delta=f"from {casc.get('brier_raw', 0):.3f} raw", delta_color="inverse")
    c[1].metric("Impact accuracy", f"{imp.get('accuracy', 0):.1%}",
                delta=f"vs {imp.get('majority_baseline', 0):.1%} baseline")
    c[2].metric("Impact macro-F1", f"{imp.get('macro_f1', 0):.3f}")
    c[2].metric("Resolution MedAE", f"{res.get('medae', 0):.0f} min",
                help="median absolute error on reliable events")

    st.markdown("---")
    st.subheader("Model portfolio")
    st.markdown("""
| Model | Task | Technique | Headline |
|---|---|---|---|
| **Cascade Classifier** | Will this escalate? | XGBoost + isotonic calibration | ROC-AUC %.3f, Brier %.3f |
| **Impact Classifier** | Severity (Low→Critical) | XGBoost, composite-severity label | acc %.1f%%, macro-F1 %.2f |
| **AFT Resolution** | How long? | XGBoost **survival:aft** (handles censoring) | MedAE %.0f min |
| **Prolonged (>60min)** | Quick vs long | XGBoost binary | in-dist AUC ~%.2f *(weak target)* |
""" % (casc.get('roc_auc', 0), casc.get('brier_calibrated', 0),
       imp.get('accuracy', 0) * 100, imp.get('macro_f1', 0), res.get('medae', 0),
       band.get('cv_auc_in_distribution', 0.59)))

    st.subheader("Methodology & honesty notes")
    st.markdown("""
- **Leakage removed:** chronological split *before* fitting; label-encoders, smoothed target
  encodings and the scaler are fit on train only. `status` is excluded (it leaks the outcome).
- **Censoring handled:** only ~74 events have a true `resolved_datetime`; the rest are
  administrative closes. The AFT model treats those as **interval-censored** and still-active
  events as **right-censored** instead of trusting or discarding them.
- **Imbalance:** cascade is ~9% positive — we report **PR-AUC** and **balanced accuracy**, not
  just accuracy, and calibrate probabilities (Brier 0.24→0.04).
- **Known limitation:** fine-grained *resolution duration* is intrinsically weak in this data
  (in-distribution AUC ~0.59, near-random out-of-time). We surface it as a historical-anchored
  estimate + duration band, and lean on cascade risk for decisions.
""")
    if casc.get('confusion_matrix'):
        st.subheader("Cascade confusion matrix (held-out)")
        cm = np.array(casc['confusion_matrix'])
        fig = px.imshow(cm, text_auto=True, color_continuous_scale='Blues',
                        x=['No cascade', 'Cascade'], y=['No cascade', 'Cascade'],
                        labels=dict(x='Predicted', y='Actual'))
        fig.update_layout(height=320, coloraxis_showscale=False)
        st.plotly_chart(fig, width='stretch')


if __name__ == '__main__':
    main()
