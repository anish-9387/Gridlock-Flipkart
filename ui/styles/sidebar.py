def get_sidebar_css():
    return '''

/* Fix sidebar logo */
section[data-testid="stSidebar"] .sidebar-logo {
  padding: 0 1rem 3rem 1rem;
  display: flex;
  justify-content: flex-start;
  align-items: center;
}

section[data-testid="stSidebar"] .sidebar-logo img {
  width: 110px !important;
  height: auto !important;
}

/* Fix the collapse toggle button showing raw text */
button[data-testid="collapsedControl"] {
  display: flex !important;
  align-items: center !important;
  justify-content: center !important;
  background: transparent !important;
  border: none !important;
}

button[data-testid="collapsedControl"] span,
button[data-testid="collapsedControl"] p {
  display: none !important;
}

button[data-testid="collapsedControl"]::after {
  content: "‹";
  font-size: 22px;
  font-weight: 300;
  color: var(--text-muted);
  line-height: 1;
  display: block;
}

section[data-testid="stSidebar"][aria-expanded="false"] ~ div button[data-testid="collapsedControl"]::after {
  content: "›";
}

section[data-testid="stSidebar"] > div:first-child {
  padding-top: 0 !important;
}

section[data-testid="stSidebar"] [data-testid="stSidebarContent"] {
  padding-top: 0 !important;
}

/* Kill any remaining top margin/gap */
section[data-testid="stSidebar"] .element-container:first-child {
  margin-top: 0 !important;
  padding-top: 0 !important;
}

section[data-testid="stSidebar"] {
  background-color: var(--bg-sidebar);
  border-right: 1px solid var(--border);
}

/* Divider */
section[data-testid="stSidebar"] hr {
  margin: 1rem 0;
  border-color: var(--border);
}

/* Remove Streamlit spacing */
section[data-testid="stSidebar"] .element-container {
  margin: 0 !important;
  padding: 0 !important;
}

section[data-testid="stSidebar"] [data-testid="stVerticalBlock"] {
  gap: 0 !important;
}

/* Navigation buttons */
section[data-testid="stSidebar"] .stButton {
  margin: 2px 0 !important;
}

section[data-testid="stSidebar"] .stButton > button {
  width: 100%;
  min-height: 40px !important;

  background: transparent;
  border: none;
  border-radius: 8px;

  padding: 8px 12px !important;

  font-size: 14px;
  font-weight: 500;
  color: var(--text-secondary);

  text-align: left !important;

  cursor: pointer;
  box-shadow: none !important;

  line-height: 1.3;

  position: relative;

  display: flex;
  align-items: center;
  justify-content: flex-start !important;
}

section[data-testid="stSidebar"] .stButton > button > div {
  width: 100%;
  text-align: left !important;
  justify-content: flex-start !important;
}

/* Hover */
section[data-testid="stSidebar"] .stButton > button:hover {
  background: var(--bg-hover);
  color: var(--text-primary);
}

/* Active page */
section[data-testid="stSidebar"] .stButton > button[kind="primary"] {
  background: var(--nav-active-bg);
  color: var(--nav-active-text) !important;
  font-weight: 600;
}

section[data-testid="stSidebar"] .stButton > button[kind="primary"]::before {
  content: "";
  position: absolute;

  left: 0;
  top: 8px;
  bottom: 8px;

  width: 4px;

  background: var(--nav-active-bar);
  border-radius: 0 3px 3px 0;
}

/* SECTION GROUPING */
section[data-testid="stSidebar"] .stMarkdown:has(p) {
  margin-top: 28px !important;
  margin-bottom: 10px !important;
}

section[data-testid="stSidebar"] .stMarkdown p {
  font-size: 11px;
  font-weight: 700;
  color: var(--text-muted);

  letter-spacing: 0.08em;
  text-transform: uppercase;

  margin: 0 !important;
  padding: 0;
}

/* Add space only after headers */
section[data-testid="stSidebar"] .stMarkdown + div {
  margin-top: 28px !important;
  margin-bottom: 12px;
}

/* Metrics */
section[data-testid="stSidebar"] div[data-testid="stMetric"] {
  background: transparent;
  border: none;
  padding: 0.25rem 0;
}

section[data-testid="stSidebar"] div[data-testid="stMetric"] label {
  color: var(--text-muted);
  font-size: 0.75rem;
}

section[data-testid="stSidebar"] div[data-testid="stMetric"] div[data-testid="stMetricValue"] {
  font-size: 1rem;
  color: var(--text-primary);
}

/* Sidebar text */
section[data-testid="stSidebar"] strong {
  color: var(--text-secondary);
  font-size: 0.82rem;
  font-weight: 600;
  letter-spacing: normal;
}
'''