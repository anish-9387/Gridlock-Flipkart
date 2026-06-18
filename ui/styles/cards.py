def get_cards_css():
    return '''
div[data-testid="stMetric"] {
  background-color: #FFFFFF;
  border: 1px solid #ECE7E1;
  border-radius: 14px;
  padding: 1.25rem 1.5rem;
  min-height: 110px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.03);
}

div[data-testid="stMetric"] label {
  color: #6B7280;
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  margin-bottom: 0.25rem;
}

div[data-testid="stMetric"] div[data-testid="stMetricValue"] {
  color: #111827;
  font-size: 1.5rem;
  font-weight: 700;
  letter-spacing: -0.02em;
  line-height: 1.3;
}

div[data-testid="stMetric"] div[data-testid="stMetricDelta"] {
  font-size: 0.8rem;
  font-weight: 400;
}

div.stPlotlyChart {
  background: #FFFFFF;
  border: 1px solid #ECE7E1;
  border-radius: 14px;
  padding: 4px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.03);
  overflow: hidden;
}

div[data-testid="stExpander"] {
  background-color: #FFFFFF;
  border: 1px solid #E5E2DC;
  border-radius: 8px;
}

div[data-testid="stExpander"] summary {
  font-weight: 500;
  color: #111827;
}

.stTabs {
  background-color: #FFFFFF;
  border-radius: 8px;
  padding: 0.25rem 0.25rem 0;
}

.stTabs button {
  color: #9CA3AF;
  font-size: 0.88rem;
}

.stTabs button:hover {
  color: #111827;
}

.stTabs button[aria-selected="true"] {
  color: #E85D2A;
  border-bottom: 2px solid #E85D2A;
}'''
