"""
CascadeIQ — Event Impact Forecasting & Response Intelligence System
Gridlock-Flipkart 2.0 Hackathon
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import matplotlib.pyplot as plt
import os
import sys
import json
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

st.set_page_config(
    page_title="CascadeIQ — Event Impact Intelligence",
    page_icon="🚦",
    layout="wide",
    initial_sidebar_state="expanded"
)

sys.path.insert(0, os.path.dirname(__file__))

from src.feature_engineering import engineer_features, ENGINEERED_FEATURE_COLS
from src.models import load_model, predict_resolution
from src.hotspot_detection import load_hotspot_models
from src.vulnerability import compute_junction_vulnerability, get_fragile_junctions
from src.similarity import load_similarity_engine, find_similar_events
from src.resources import recommend_resources, IMPACT_RESOURCE_MAP
from src.cascade_autopsy import estimate_point_of_no_return, generate_timeline
from src.digital_twin import run_scenario, compare_scenarios, scenarios_to_dataframe
from src.knowledge_graph import build_event_graph, get_graph_stats

MODELS_DIR = os.path.join(os.path.dirname(__file__), 'models')
DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')


@st.cache_resource
def load_all_models():
    impact_model = load_model('impact_classifier')
    res_model = load_model('resolution_regressor')
    cascade_model = load_model('cascade_classifier')
    vectorizer, tfidf_matrix, event_data = load_similarity_engine()
    hotspots = load_hotspot_models()
    return impact_model, res_model, cascade_model, vectorizer, tfidf_matrix, event_data, hotspots


@st.cache_data
def load_dataset():
    path = os.path.join(os.path.dirname(__file__), 'data', 'dataset.csv')
    df = pd.read_csv(path, low_memory=False)
    return df


@st.cache_data
def compute_features_and_vulnerability(df):
    X, y_res, y_impact, encoders, scaler, feat_cols = engineer_features(df, is_train=True)
    df_feat = df.copy()
    df_feat['resolution_minutes'] = y_res
    df_feat['impact_level'] = y_impact
    df_feat['priority_High'] = (df_feat['priority'].astype(str).str.lower().str.strip() == 'high').astype(int)
    df_feat['requires_road_closure'] = df_feat['requires_road_closure'].fillna(0).astype(int)
    vuln = compute_junction_vulnerability(df_feat)
    return df_feat, vuln, encoders, feat_cols


def get_impact_label(level):
    return {0: '🟢 Low', 1: '🟡 Medium', 2: '🟠 High', 3: '🔴 Critical'}.get(level, 'Unknown')


IMPACT_COLORS = {0: '#2ECC71', 1: '#F1C40F', 2: '#E67E22', 3: '#E74C3C'}


def main():
    st.title("🚦 CascadeIQ — Event Impact Forecasting & Response Intelligence System")
    st.markdown("### *Predicting Event Escalation Before It Becomes Gridlock*")
    st.markdown("---")

    df = load_dataset()

    impact_model, res_model, cascade_model, vectorizer, tfidf_matrix, event_data, hotspots = load_all_models()
    df_feat, junction_vuln, encoders, feat_cols = compute_features_and_vulnerability(df)

    with st.sidebar:
        st.image("https://img.icons8.com/fluency/96/traffic-jam.png", width=80)
        st.title("CascadeIQ")
        st.caption("Gridlock-Flipkart 2.0")
        st.markdown("---")

        page = st.radio(
            "Navigation",
            [
                "📊 Dashboard Overview",
                "🔮 Event Impact Prediction",
                "📍 Hotspot Analysis",
                "⚠️ Junction Vulnerability",
                "🔍 Event Similarity Search",
                "🕵️ Cascade Autopsy",
                "📋 Resource Recommendation",
                "🔄 Digital Twin Simulator",
                "🕸️ Knowledge Graph"
            ]
        )

        st.markdown("---")
        st.caption(f"Dataset: {len(df):,} events")
        st.caption(f"Junctions: {df['junction'].nunique()}")
        st.caption(f"Zones: {df['zone'].nunique()}")

        if os.path.exists(os.path.join(MODELS_DIR, 'metrics.json')):
            with open(os.path.join(MODELS_DIR, 'metrics.json')) as f:
                metrics = json.load(f)
            st.markdown("### Model Performance")
            st.metric("Impact Accuracy", f"{metrics['impact_accuracy']:.1%}")
            st.metric("Resolution MAE", f"{metrics['resolution_mae']:.0f} mins")
            st.metric("Cascade Accuracy", f"{metrics['cascade_accuracy']:.1%}")

    if page == "📊 Dashboard Overview":
        show_dashboard(df, df_feat, junction_vuln)
    elif page == "🔮 Event Impact Prediction":
        show_prediction(df, df_feat, impact_model, res_model, cascade_model, encoders, feat_cols)
    elif page == "📍 Hotspot Analysis":
        show_hotspots(df, hotspots)
    elif page == "⚠️ Junction Vulnerability":
        show_vulnerability(junction_vuln)
    elif page == "🔍 Event Similarity Search":
        show_similarity(df, event_data, vectorizer, tfidf_matrix)
    elif page == "🕵️ Cascade Autopsy":
        show_autopsy(df, df_feat, impact_model, res_model, cascade_model, encoders, feat_cols)
    elif page == "📋 Resource Recommendation":
        show_resources(df_feat)
    elif page == "🔄 Digital Twin Simulator":
        show_digital_twin(df, impact_model, res_model, cascade_model, encoders)
    elif page == "🕸️ Knowledge Graph":
        show_knowledge_graph(df_feat)


def show_dashboard(df, df_feat, junction_vuln):
    st.header("📊 Operational Dashboard")

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Events", f"{len(df):,}", delta="8173 records")
    with col2:
        active = len(df[df['status'] == 'active'])
        st.metric("Active Events", active, delta=f"{(active/len(df)*100):.1f}%")
    with col3:
        high_impact = len(df_feat[df_feat['impact_level'] >= 2])
        st.metric("High/Critical Impact", high_impact, delta=f"{(high_impact/len(df_feat)*100):.1f}%")
    with col4:
        top_junc = junction_vuln.iloc[0]['junction'] if len(junction_vuln) > 0 else "N/A"
        st.metric("Most Vulnerable", top_junc)

    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Event Type Distribution")
        type_counts = df['event_type'].value_counts()
        fig = px.pie(values=type_counts.values, names=type_counts.index,
                     color_discrete_sequence=px.colors.qualitative.Set2,
                     hole=0.4)
        fig.update_layout(height=350, margin=dict(t=0, b=0, l=0, r=0))
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("Impact Level Distribution")
        impact_counts = df_feat['impact_level'].value_counts().sort_index()
        labels = ['Low', 'Medium', 'High', 'Critical']
        colors = [IMPACT_COLORS[i] for i in impact_counts.index]
        fig = px.bar(x=labels, y=impact_counts.values,
                     color=labels, color_discrete_sequence=colors)
        fig.update_layout(height=350, xaxis_title="Impact Level",
                         yaxis_title="Count", showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Top Event Causes")
        cause_counts = df['event_cause'].value_counts().head(8)
        fig = px.bar(y=cause_counts.index, x=cause_counts.values,
                     orientation='h', color=cause_counts.values,
                     color_continuous_scale='YlOrRd')
        fig.update_layout(height=350, xaxis_title="Count", yaxis_title="")
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("Events by Corridor")
        corr_counts = df['corridor'].value_counts().head(10)
        fig = px.bar(y=corr_counts.index, x=corr_counts.values,
                     orientation='h', color=corr_counts.values,
                     color_continuous_scale='Blues')
        fig.update_layout(height=350, xaxis_title="Count", yaxis_title="")
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")
    st.subheader("📈 Time Series: Events Over Time")
    dates = pd.to_datetime(df['start_datetime'], utc=True, errors='coerce')
    daily_counts = dates.dt.date.value_counts().sort_index()
    fig = px.line(x=list(daily_counts.index), y=daily_counts.values,
                  labels={'x': 'Date', 'y': 'Event Count'})
    fig.update_layout(height=350)
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")
    st.subheader("🏆 Top 10 Most Vulnerable Junctions")
    col_config = {
        'junction': 'Junction',
        'risk_score': 'Risk Score (/10)',
        'risk_category': 'Category',
        'event_count': 'Events',
        'avg_resolution_minutes': 'Avg Resolution (min)',
        'high_priority_ratio': 'High Priority %',
        'closure_ratio': 'Closure %'
    }
    display_df = junction_vuln.head(10)[list(col_config.keys())].copy()
    display_df.columns = list(col_config.values())
    st.dataframe(display_df, use_container_width=True, hide_index=True)


def show_prediction(df, df_feat, impact_model, res_model, cascade_model, encoders, feat_cols):
    st.header("🔮 Event Impact Prediction")
    st.markdown("Predict impact level, resolution time, and cascade probability for a new event.")

    with st.form("prediction_form"):
        col1, col2 = st.columns(2)

        with col1:
            event_type = st.selectbox("Event Type", ['unplanned', 'planned'])
            event_cause = st.selectbox(
                "Event Cause",
                ['vehicle_breakdown', 'water_logging', 'tree_fall', 'accident',
                 'construction', 'public_event', 'procession', 'vip_movement',
                 'protest', 'pot_holes', 'congestion', 'road_conditions', 'others']
            )
            priority = st.selectbox("Priority", ['Low', 'High'])
            requires_road_closure = st.checkbox("Requires Road Closure")

        with col2:
            corridor = st.selectbox("Corridor", sorted(df['corridor'].dropna().unique()))
            zone = st.selectbox("Zone", sorted(df['zone'].dropna().unique()))
            junction = st.selectbox("Junction", ['Unknown'] + sorted(
                [j for j in df['junction'].dropna().unique() if j != 'unknown']))
            hour = st.slider("Hour of Day", 0, 23, 14)

        submitted = st.form_submit_button("🔮 Predict Impact", type="primary")

    if submitted:
        input_data = pd.DataFrame([{
            'event_type': event_type,
            'event_cause': event_cause,
            'priority': priority,
            'requires_road_closure': requires_road_closure,
            'corridor': corridor,
            'zone': zone,
            'junction': junction if junction != 'Unknown' else 'unknown',
            'start_datetime': pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S'),
            'resolved_datetime': None,
            'closed_datetime': None,
            'police_station': 'unknown',
            'status': 'active',
            'latitude': 12.97,
            'longitude': 77.59
        }])

        try:
            X_input, _, _, _, _ = engineer_features(
                input_data, is_train=False, target_encoders=encoders
            )
        except Exception as e:
            st.error(f"Feature engineering error: {e}")
            return

        impact_pred = impact_model.predict(X_input)[0]
        impact_proba = impact_model.predict_proba(X_input)[0]

        res_pred = predict_resolution(res_model, X_input)[0]

        cascade_pred = cascade_model.predict(X_input)[0]
        cascade_proba = cascade_model.predict_proba(X_input)[0]

        resources = recommend_resources(
            impact_pred, event_cause, requires_road_closure, corridor, hour
        )

        st.markdown("---")
        st.subheader("📊 Prediction Results")

        impact_label = get_impact_label(impact_pred)
        confidence = float(max(impact_proba) * 100)

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Impact Level", impact_label)
        with col2:
            st.metric("Confidence", f"{confidence:.1f}%")
        with col3:
            st.metric("Expected Resolution", f"{res_pred:.0f} mins")
        with col4:
            cascade_risk = "High 🚨" if cascade_pred == 1 else "Low ✅"
            st.metric("Cascade Risk", cascade_risk,
                      delta=f"{cascade_proba[1]*100:.1f}% probability")

        st.markdown("---")
        st.subheader("📋 Resource Recommendation")

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Officers Required", resources['officers'])
        with col2:
            st.metric("Barricades Required", resources['barricades'])
        with col3:
            st.metric("Monitoring", resources['monitoring'])
        with col4:
            st.metric("Diversion", resources['diversion'])

        st.info(f"**{resources['description']}**")

        st.markdown("---")
        st.subheader("📈 Impact Probability Distribution")

        proba_df = pd.DataFrame({
            'Impact': ['Low', 'Medium', 'High', 'Critical'],
            'Probability': impact_proba * 100
        })
        fig = px.bar(proba_df, x='Impact', y='Probability',
                     color='Impact',
                     color_discrete_map={
                         'Low': '#2ECC71', 'Medium': '#F1C40F',
                         'High': '#E67E22', 'Critical': '#E74C3C'
                     },
                     text_auto='.1f')
        fig.update_layout(height=350, yaxis_title="Probability (%)")
        fig.update_traces(texttemplate='%{text}%', textposition='outside')
        st.plotly_chart(fig, use_container_width=True)


def show_hotspots(df, hotspots):
    st.header("📍 Hotspot Analysis")
    st.markdown("Spatial clustering of events to identify recurring incident zones.")

    cause_options = list(hotspots.keys()) if hotspots else ['No hotspots found']
    selected_cause = st.selectbox("Select Event Cause", cause_options)

    if hotspots and selected_cause in hotspots:
        hotspot_df = hotspots[selected_cause]

        st.subheader(f"Hotspot Clusters for: {selected_cause}")
        st.dataframe(hotspot_df, use_container_width=True, hide_index=True)

        fig = px.scatter_mapbox(
            df[df['event_cause'] == selected_cause].dropna(subset=['latitude', 'longitude']).head(500),
            lat='latitude', lon='longitude',
            color='priority', size_max=10, zoom=11,
            mapbox_style='carto-positron',
            title=f"Event Locations: {selected_cause}"
        )
        for _, row in hotspot_df.iterrows():
            fig.add_trace(go.Scattermapbox(
                lat=[row['avg_lat']],
                lon=[row['avg_lon']],
                mode='markers+text',
                marker=dict(size=row['count'] * 3, color='red', opacity=0.7),
                text=[f"Cluster: {row['count']} events"],
                textposition='top center',
                name=f"Hotspot ({row['count']} events)"
            ))
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")
    st.subheader("Overall Event Map")
    map_df = df.dropna(subset=['latitude', 'longitude']).copy()
    map_df['impact_category'] = pd.cut(
        map_df['priority'].map({'High': 2, 'Low': 1}).fillna(1),
        bins=[0, 1, 2], labels=['Low Priority', 'High Priority']
    )

    fig = px.scatter_mapbox(
        map_df.sample(min(2000, len(map_df))),
        lat='latitude', lon='longitude',
        color='event_cause', size_max=8, zoom=10,
        mapbox_style='carto-positron',
        title="All Events (sampled)"
    )
    st.plotly_chart(fig, use_container_width=True)


def show_vulnerability(junction_vuln):
    st.header("⚠️ Junction Vulnerability Analysis")
    st.markdown("Identify junctions most at risk during events.")

    col1, col2 = st.columns([2, 1])
    with col1:
        top_n = st.slider("Number of junctions to display", 5, 50, 20)
    with col2:
        min_events = st.number_input("Minimum events", 1, 100, 5)

    filtered = junction_vuln[junction_vuln['event_count'] >= min_events].copy()
    display_df = filtered.head(top_n)

    st.subheader(f"Top {top_n} Vulnerable Junctions (min {min_events} events)")

    fig = px.bar(
        display_df.head(15),
        x='junction', y='risk_score',
        color='risk_category',
        color_discrete_map={
            'Low': '#2ECC71', 'Medium': '#F1C40F',
            'High': '#E67E22', 'Critical': '#E74C3C'
        },
        text_auto='.1f',
        title="Junction Risk Scores"
    )
    fig.update_layout(height=450, xaxis_tickangle=-45)
    st.plotly_chart(fig, use_container_width=True)

    col_config = {
        'junction': 'Junction',
        'risk_score': 'Risk Score (/10)',
        'risk_category': 'Category',
        'event_count': 'Events',
        'avg_resolution_minutes': 'Avg Resolution (min)',
        'high_priority_ratio': 'High Priority %',
        'closure_ratio': 'Closure %'
    }
    display_cols = [c for c in col_config.keys() if c in display_df.columns]
    show_df = display_df[display_cols].copy()
    show_df.columns = [col_config[c] for c in display_cols]
    st.dataframe(show_df, use_container_width=True, hide_index=True)

    st.markdown("---")
    st.subheader("📊 Vulnerability Distribution")

    cat_counts = filtered['risk_category'].value_counts()
    fig = px.pie(
        values=cat_counts.values, names=cat_counts.index,
        color=cat_counts.index,
        color_discrete_map={
            'Low': '#2ECC71', 'Medium': '#F1C40F',
            'High': '#E67E22', 'Critical': '#E74C3C'
        },
        hole=0.4,
        title="Junction Risk Category Distribution"
    )
    st.plotly_chart(fig, use_container_width=True)


def show_similarity(df, event_data, vectorizer, tfidf_matrix):
    st.header("🔍 Event Similarity Search")
    st.markdown("Find historical events similar to a given event.")

    with st.form("similarity_form"):
        col1, col2 = st.columns(2)
        with col1:
            s_event_type = st.selectbox("Event Type", ['unplanned', 'planned'], key='sim_type')
            s_cause = st.selectbox("Event Cause", sorted(df['event_cause'].dropna().unique()), key='sim_cause')
            s_priority = st.selectbox("Priority", ['Low', 'High'], key='sim_priority')
        with col2:
            s_corridor = st.selectbox("Corridor", ['Non-corridor'] + sorted(
                [c for c in df['corridor'].dropna().unique() if c != 'Non-corridor']), key='sim_corridor')
            s_zone = st.selectbox("Zone", sorted(df['zone'].dropna().unique()), key='sim_zone')
            s_junction = st.selectbox("Junction", ['unknown'] + sorted(
                df['junction'].dropna().unique().tolist()), key='sim_junction')

        submitted = st.form_submit_button("🔍 Find Similar Events", type="primary")

    if submitted and event_data is not None and vectorizer is not None:
        query = {
            'event_cause': s_cause,
            'corridor': s_corridor,
            'zone': s_zone,
            'junction': s_junction,
            'event_type': s_event_type,
            'priority': s_priority,
            'police_station': 'unknown'
        }

        results = find_similar_events(query, vectorizer, tfidf_matrix, event_data, top_k=5)

        if results:
            st.subheader("Top 5 Most Similar Historical Events")
            st.caption("Similarity based on event characteristics (cause, location, type, priority)")

            for i, r in enumerate(results):
                impact = get_impact_label(r['impact_level'])
                with st.container():
                    cols = st.columns([0.1, 0.6, 0.3])
                    with cols[0]:
                        st.markdown(f"### {i + 1}")
                    with cols[1]:
                        st.markdown(f"**Cause:** {r['event_cause']} | **Corridor:** {r['corridor']} | **Zone:** {r['zone']}")
                        st.markdown(f"**Junction:** {r.get('junction', 'N/A')} | **Priority:** {r['priority']}")
                    with cols[2]:
                        st.markdown(f"**Similarity:** {r['similarity_score']:.0%}")
                        st.markdown(f"**Impact:** {impact}")
                        st.markdown(f"**Resolution:** {r.get('resolution_minutes', 'N/A')} mins")

                    if i < len(results) - 1:
                        st.divider()
        else:
            st.warning("No similar events found.")

    elif event_data is None:
        st.warning("Similarity engine not available. Please train the model first.")


def show_autopsy(df, df_feat, impact_model, res_model, cascade_model, encoders, feat_cols):
    st.header("🕵️ Cascade Autopsy — Counterfactual Analysis")
    st.markdown("**Discover the exact decision window where intervention could have prevented escalation.**")

    resolved_df = df_feat[df_feat['status'].isin(['closed', 'resolved'])].dropna(
        subset=['resolution_minutes']).copy()
    resolved_df = resolved_df[resolved_df['resolution_minutes'] > 10]
    resolved_df = resolved_df[resolved_df['resolution_minutes'] < 1440]

    event_options = resolved_df.head(100)[['id', 'event_cause', 'corridor', 'junction',
                                            'resolution_minutes', 'priority']].copy()
    event_options['label'] = event_options.apply(
        lambda r: f"[{r['id']}] {r['event_cause']} @ {r.get('junction', '?')} ({r['resolution_minutes']:.0f} mins)",
        axis=1
    )

    selected_label = st.selectbox("Select a historical event for autopsy", event_options['label'].tolist())
    selected_id = selected_label.split(']')[0].replace('[', '').strip()

    if st.button("🔬 Run Cascade Autopsy", type="primary"):
        event_row = resolved_df[resolved_df['id'] == selected_id]

        if len(event_row) == 0:
            st.error("Event not found.")
            return

        event_row = event_row.iloc[0]

        impact = get_impact_label(event_row['impact_level'])
        st.subheader(f"Event: {event_row['event_cause']} @ {event_row.get('junction', 'N/A')}")
        st.caption(f"Actual Impact: {impact} | Resolution: {event_row['resolution_minutes']:.0f} mins")

        X_event = pd.DataFrame([event_row.to_dict()])
        try:
            X_input, _, _, _, _ = engineer_features(
                X_event, is_train=False, target_encoders=encoders
            )
        except Exception as e:
            st.error(f"Feature extraction error: {e}")
            return

        pred_impact = impact_model.predict(X_input)[0]
        pred_res = predict_resolution(res_model, X_input)[0]

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Actual Impact", impact)
        with col2:
            st.metric("Predicted Resolution", f"{pred_res:.0f} mins")
        with col3:
            st.metric("Actual Resolution", f"{event_row['resolution_minutes']:.0f} mins")

        autopsy = estimate_point_of_no_return(
            event_row.to_dict(), impact_model, engineer_features, encoders
        )

        st.markdown("---")
        if autopsy:
            st.subheader("🔍 Cascade Autopsy Results")
            st.success("**Cascade Was Preventable!**")

            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Point of No Return",
                         autopsy['point_of_no_return_time'],
                         delta=f"{autopsy['point_of_no_return_minutes']:.0f} min after start")
            with col2:
                st.metric("Decision Window",
                         f"{autopsy['decision_window_minutes']} minutes",
                         delta="Intervene here!")
            with col3:
                st.metric("Potential Delay Saved",
                         f"{autopsy['potential_delay_saved']} minutes",
                         delta="~60% reduction")

            st.markdown("---")
            st.subheader("⏱️ Reality vs Counterfactual Timeline")

            col1, col2 = st.columns(2)
            with col1:
                st.markdown("#### ❌ Reality")
                reality_timeline = [
                    f"**{autopsy['event_start']}** — Event Started",
                    f"**{autopsy['point_of_no_return_time']}** — ❌ Point of No Return (missed)",
                    f"**{autopsy['event_start_dt'][11:16]}** — Congestion peaks",
                    f"**Resolved at +{autopsy['actual_resolution_minutes']}min** — Gridlock"
                ]
                for item in reality_timeline:
                    st.markdown(f"- {item}")

            with col2:
                st.markdown("#### ✅ Counterfactual (What If)")
                decision_time = (pd.to_datetime(autopsy['event_start_dt']) +
                                timedelta(minutes=autopsy['point_of_no_return_minutes']))
                intervention_time = decision_time - timedelta(minutes=5)
                cf_timeline = [
                    f"**{autopsy['event_start']}** — Event Started",
                    f"**{intervention_time.strftime('%H:%M')}** — ⚡ Intervention Activated",
                    f"**{autopsy['point_of_no_return_time']}** — 🛑 Cascade Stopped",
                    f"**Resolved at +{autopsy['potential_delay_saved']}min** — Normal Flow"
                ]
                for item in cf_timeline:
                    st.markdown(f"- {item}")

        timeline = generate_timeline(event_row.to_dict(), autopsy)
        if timeline:
            st.markdown("---")
            st.subheader("⏳ Event Timeline")
            for t in timeline:
                if t['type'] == 'critical':
                    st.error(f"**{t['time']}** — {t['event']}")
                elif t['type'] == 'escalation':
                    st.warning(f"**{t['time']}** — {t['event']}")
                elif t['type'] == 'active':
                    st.info(f"**{t['time']}** — {t['event']}")
                else:
                    st.info(f"**{t['time']}** — {t['event']}")


def show_resources(df_feat):
    st.header("📋 Resource Recommendation Engine")
    st.markdown("Get data-driven resource recommendations for event management.")

    col1, col2 = st.columns(2)
    with col1:
        r_event_cause = st.selectbox("Event Cause",
            ['vehicle_breakdown', 'water_logging', 'tree_fall', 'accident',
             'construction', 'public_event', 'procession', 'vip_movement',
             'protest', 'pot_holes', 'congestion', 'road_conditions', 'others'])
        r_priority = st.selectbox("Priority", ['Low', 'High'])
    with col2:
        r_corridor = st.selectbox("Corridor",
            ['Non-corridor', 'ORR East 1', 'ORR North 1', 'Bellary Road 1',
             'Tumkur Road', 'Mysore Road', 'Hosur Road', 'Magadi Road',
             'Old Madras Road', 'Bannerghata Road'])
        r_hour = st.slider("Hour of Day", 0, 23, 14)
        r_closure = st.checkbox("Requires Road Closure")

    if st.button("📋 Get Recommendations", type="primary"):
        r_impact_level = 2 if r_priority == 'High' else 0
        if r_event_cause in ['public_event', 'procession']:
            r_impact_level = max(r_impact_level, 2)
        if r_closure:
            r_impact_level = min(r_impact_level + 1, 3)

        resources = recommend_resources(
            r_impact_level, r_event_cause, r_closure, r_corridor, r_hour
        )

        st.markdown("---")
        st.subheader("📊 Recommended Resource Deployment")

        impact_label = get_impact_label(r_impact_level)
        st.metric("Predicted Impact Level", impact_label)

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("👮 Officers", resources['officers'],
                     help="Number of traffic police officers needed")
        with col2:
            st.metric("🚧 Barricades", resources['barricades'],
                     help="Number of barricades needed")
        with col3:
            st.metric("📡 Monitoring", resources['monitoring'],
                     help="Monitoring priority level")
        with col4:
            st.metric("🔄 Diversion", resources['diversion'],
                     help="Diversion planning requirement")

        st.info(f"**{resources['description']}**")

        st.markdown("---")
        st.subheader("📈 Resource Allocation Reference")
        ref_data = []
        for level, info in IMPACT_RESOURCE_MAP.items():
            ref_data.append({
                'Impact': info['impact'],
                'Officers': info['officers'],
                'Barricades': info['barricades'],
                'Monitoring': info['monitoring'],
                'Diversion': info['diversion']
            })
        ref_df = pd.DataFrame(ref_data)
        st.dataframe(ref_df, use_container_width=True, hide_index=True)

        st.markdown("---")
        st.subheader("📊 Resource Comparison")
        impacts = ['Low', 'Medium', 'High', 'Critical']
        officers_base = [2, 5, 10, 15]
        barricades_base = [2, 6, 14, 20]

        fig = go.Figure()
        fig.add_trace(go.Bar(name='Officers', x=impacts, y=officers_base,
                            marker_color='#3498DB'))
        fig.add_trace(go.Bar(name='Barricades', x=impacts, y=barricades_base,
                            marker_color='#E74C3C'))
        fig.update_layout(barmode='group', height=400,
                         title="Default Resource Requirements by Impact Level")
        st.plotly_chart(fig, use_container_width=True)

        st.markdown("---")
        st.info("""
        **How resources are calculated:**
        - Base resources are determined by impact level
        - Event cause modifiers adjust officer/barricade counts
        - Peak hours (8-10 AM, 5-8 PM) increase requirements by 20%
        - Road closure increases barricade needs by 50%
        - Major corridors add 10% to resource requirements
        """)
        
        
def show_digital_twin(df, impact_model, res_model, cascade_model, encoders):
    st.header("🔄 Traffic Digital Twin Simulator")
    st.markdown("**Compare multiple event scenarios side-by-side to assess impact before it happens.**")

    df = load_dataset()

    if 'scenarios' not in st.session_state:
        st.session_state.scenarios = []
    if 'scenario_results' not in st.session_state:
        st.session_state.scenario_results = []

    with st.expander("➕ Add a Scenario", expanded=len(st.session_state.scenarios) == 0):
        with st.form("scenario_form"):
            col1, col2 = st.columns(2)
            with col1:
                scenario_name = st.text_input("Scenario Name", value=f"Scenario {len(st.session_state.scenarios) + 1}")
                twin_event_type = st.selectbox("Event Type", ['unplanned', 'planned'], key='twin_type')
                twin_event_cause = st.selectbox(
                    "Event Cause",
                    ['vehicle_breakdown', 'water_logging', 'tree_fall', 'accident',
                     'construction', 'public_event', 'procession', 'vip_movement',
                     'protest', 'pot_holes', 'congestion', 'road_conditions', 'others'],
                    key='twin_cause'
                )
                twin_priority = st.selectbox("Priority", ['Low', 'High'], key='twin_priority')
            with col2:
                twin_corridor = st.selectbox("Corridor", sorted(df['corridor'].dropna().unique()), key='twin_corridor')
                twin_zone = st.selectbox("Zone", sorted(df['zone'].dropna().unique()), key='twin_zone')
                twin_junction = st.selectbox("Junction", ['Unknown'] + sorted(
                    [j for j in df['junction'].dropna().unique() if j != 'unknown']), key='twin_junction')
                twin_hour = st.slider("Hour of Day", 0, 23, 14, key='twin_hour')
                twin_closure = st.checkbox("Requires Road Closure", key='twin_closure')

            if st.form_submit_button("➕ Add to Comparison", type="primary"):
                params = {
                    'name': scenario_name,
                    'event_type': twin_event_type,
                    'event_cause': twin_event_cause,
                    'priority': twin_priority,
                    'requires_road_closure': twin_closure,
                    'corridor': twin_corridor,
                    'zone': twin_zone,
                    'junction': twin_junction,
                    'hour': twin_hour
                }
                st.session_state.scenarios.append(params)
                st.rerun()

    if st.session_state.scenarios:
        st.markdown("### 🎯 Scenarios Queued for Comparison")

        for i, s in enumerate(st.session_state.scenarios):
            loc_display = s['junction'] if s['junction'] != 'Unknown' else f"{s['corridor']}"
            cols = st.columns([0.05, 0.25, 0.2, 0.2, 0.25, 0.05])
            with cols[0]:
                st.write(f"{i + 1}")
            with cols[1]:
                st.write(f"**{s['name']}**")
            with cols[2]:
                st.write(f"{s['event_cause']}")
            with cols[3]:
                st.write(f"{s['priority']} priority")
            with cols[4]:
                st.write(f"📍 {loc_display}")
            with cols[5]:
                if st.button("✕", key=f"remove_scenario_{i}"):
                    st.session_state.scenarios.pop(i)
                    st.session_state.scenario_results = []
                    st.rerun()

        col1, col2 = st.columns([1, 5])
        with col1:
            if st.button("🔄 Run Comparison", type="primary"):
                with st.spinner("Simulating scenarios..."):
                    st.session_state.scenario_results = compare_scenarios(
                        st.session_state.scenarios, impact_model, res_model, cascade_model, encoders
                    )
                st.rerun()

        with col2:
            if st.session_state.scenario_results:
                if st.button("🗑️ Clear All"):
                    st.session_state.scenarios = []
                    st.session_state.scenario_results = []
                    st.rerun()

    if st.session_state.scenario_results:
        st.markdown("### 📊 Scenario Comparison Results")

        results_df = scenarios_to_dataframe(st.session_state.scenario_results)
        st.dataframe(results_df, use_container_width=True, hide_index=True)

        chart_df = results_df.copy()
        chart_df['Resolution (min)'] = pd.to_numeric(chart_df['Resolution (min)'], errors='coerce')

        color_map = {'Low': '#2ECC71', 'Medium': '#F1C40F', 'High': '#E67E22', 'Critical': '#E74C3C'}
        chart_df['color'] = chart_df['Impact Level'].map(color_map).fillna('#95A5A6')
        chart_df['label'] = chart_df.apply(
            lambda r: f"{r['Impact Level']}<br>{r['Resolution (min)']:.0f} min", axis=1)

        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=chart_df['Scenario'].tolist(),
            y=chart_df['Resolution (min)'].tolist(),
            text=chart_df['label'].tolist(),
            textposition='inside',
            marker_color=chart_df['color'].tolist()
        ))
        fig.update_layout(
            title="Resolution Time by Scenario",
            yaxis_title="Minutes",
            height=400
        )
        st.plotly_chart(fig, use_container_width=True)

        with st.expander("📈 Detailed Comparison by Metric"):
            metric_chart_df = results_df.copy()
            for col in ['Resolution (min)', 'Confidence', 'Cascade Prob.']:
                if col in metric_chart_df.columns:
                    metric_chart_df[col] = pd.to_numeric(
                        metric_chart_df[col].astype(str).str.rstrip('%'), errors='coerce'
                    )

            fig2 = go.Figure()
            for col in ['Resolution (min)', 'Confidence', 'Cascade Prob.']:
                if col in metric_chart_df.columns:
                    fig2.add_trace(go.Bar(
                        name=col,
                        x=metric_chart_df['Scenario'],
                        y=metric_chart_df[col],
                        text=[f"{v:.1f}" if isinstance(v, (int, float)) else str(v) for v in metric_chart_df[col]],
                        textposition='outside'
                    ))
            fig2.update_layout(
                title="Multi-Metric Scenario Comparison",
                yaxis_title="Value",
                barmode='group',
                height=400
            )
            st.plotly_chart(fig2, use_container_width=True)


def show_knowledge_graph(df_feat):
    st.header("🕸️ Knowledge Graph — Event Relationship Analysis")
    st.markdown("**Explore multi-dimensional relationships between events based on shared cause, location, and type.**")

    with st.sidebar:
        st.subheader("Knowledge Graph Filters")
        max_nodes = st.slider("Max Events", 20, 100, 50, key='kg_nodes')
        min_sim = st.slider("Min Similarity", 0.05, 0.8, 0.2, 0.05, key='kg_sim')
        causes = ['All'] + sorted(df_feat['event_cause'].dropna().unique().tolist())
        selected_cause = st.selectbox("Event Cause", causes, key='kg_cause')
        zones = ['All'] + sorted(df_feat['zone'].dropna().unique().tolist())
        selected_zone = st.selectbox("Zone", zones, key='kg_zone')
        color_by = st.selectbox("Color Nodes By", ['event_cause', 'impact_level', 'priority', 'zone'],
                                key='kg_color')

    with st.spinner("Building knowledge graph..."):
        nodes_df, edges_df = build_event_graph(
            df_feat, max_nodes=max_nodes, min_similarity=min_sim,
            filter_cause=selected_cause, filter_zone=selected_zone
        )

    if nodes_df.empty:
        st.warning("Not enough connected events to build a graph. Try increasing max events or lowering the similarity threshold.")
        return

    stats = get_graph_stats(nodes_df, edges_df)
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Events (Nodes)", stats['nodes'])
    with col2:
        st.metric("Connections (Edges)", stats['edges'])
    with col3:
        st.metric("Clusters", stats['clusters'])
    with col4:
        st.metric("Avg Connections/Event", stats['avg_degree'])

    edge_traces = []
    if not edges_df.empty:
        edge_x = []
        edge_y = []
        for _, e in edges_df.iterrows():
            src = nodes_df[nodes_df['id'] == e['source']].iloc[0]
            tgt = nodes_df[nodes_df['id'] == e['target']].iloc[0]
            edge_x.extend([src['x'], tgt['x'], None])
            edge_y.extend([src['y'], tgt['y'], None])
        edge_traces.append(go.Scatter(
            x=edge_x, y=edge_y,
            mode='lines',
            line=dict(width=0.5, color='#888'),
            hoverinfo='none',
            showlegend=False
        ))

    if color_by == 'impact_level':
        nodes_df['color_group'] = nodes_df['impact_level'].map({0: 'Low', 1: 'Medium', 2: 'High', 3: 'Critical'})
    else:
        nodes_df['color_group'] = nodes_df[color_by]

    color_palette = px.colors.qualitative.Set2 + px.colors.qualitative.Set3
    unique_groups = nodes_df['color_group'].unique()
    group_colors = {g: color_palette[i % len(color_palette)] for i, g in enumerate(sorted(unique_groups))}
    node_colors = nodes_df['color_group'].map(group_colors).tolist()

    def fmt_location(r):
        parts = []
        if r['junction'] != 'unknown':
            parts.append(r['junction'])
        if r['corridor'] != 'unknown':
            parts.append(r['corridor'])
        if r['zone'] != 'unknown':
            parts.append(r['zone'])
        return ', '.join(parts) if parts else 'Unknown'

    node_labels = nodes_df.apply(
        lambda r: r['corridor'] if r['corridor'] != 'unknown'
                  else (r['zone'] if r['zone'] != 'unknown' else ''),
        axis=1
    ).tolist()

    node_trace = go.Scatter(
        x=nodes_df['x'], y=nodes_df['y'],
        mode='markers+text',
        text=node_labels,
        textposition='top center',
        textfont=dict(size=8, color='#333'),
        marker=dict(
            size=nodes_df['degree'].clip(lower=5, upper=25).tolist(),
            color=node_colors,
            line=dict(width=1, color='#333'),
            opacity=0.85
        ),
        customdata=nodes_df.apply(
            lambda r: [
                r['event_cause'],
                fmt_location(r),
                r['priority'],
                ['Low', 'Medium', 'High', 'Critical'][min(int(r['impact_level']), 3)],
                f"{r['resolution_minutes']:.0f}",
                str(r['degree'])
            ],
            axis=1
        ).tolist(),
        hovertemplate=(
            "<b>%{customdata[0]}</b><br>"
            "📍 %{customdata[1]}<br>"
            "Priority: %{customdata[2]}<br>"
            "Impact: %{customdata[3]} | Resolution: %{customdata[4]} min<br>"
            "Connections: %{customdata[5]}<extra></extra>"
        ),
        showlegend=False
    )

    fig = go.Figure(data=edge_traces + [node_trace])
    fig.update_layout(
        title=f"Knowledge Graph — {stats['nodes']} events, {stats['edges']} connections, {stats['clusters']} clusters",
        showlegend=False,
        hovermode='closest',
        height=600,
        xaxis=dict(showgrid=False, zeroline=False, visible=False),
        yaxis=dict(showgrid=False, zeroline=False, visible=False),
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=10, r=10, t=40, b=10)
    )
    st.plotly_chart(fig, use_container_width=True)

    with st.expander("📋 Node Details"):
        display_cols = ['event_cause', 'corridor', 'zone', 'junction', 'priority',
                        'event_type', 'impact_level', 'resolution_minutes', 'degree']
        display_map = {
            'event_cause': 'Cause', 'corridor': 'Corridor', 'zone': 'Zone',
            'junction': 'Junction', 'priority': 'Priority', 'event_type': 'Type',
            'impact_level': 'Impact', 'resolution_minutes': 'Resolution (min)', 'degree': 'Connections'
        }
        details_df = nodes_df[[c for c in display_cols if c in nodes_df.columns]].copy()
        if 'impact_level' in details_df.columns:
            details_df['impact_level'] = details_df['impact_level'].map(
                {0: 'Low', 1: 'Medium', 2: 'High', 3: 'Critical'})
        details_df.columns = [display_map.get(c, c) for c in details_df.columns]
        st.dataframe(details_df, use_container_width=True, hide_index=True)


if __name__ == '__main__':
    main()
