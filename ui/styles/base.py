def get_base_css():
    return '''@import url('https://api.fontshare.com/v2/css?f[]=geist@400,500,600,700&display=swap');
@import url('https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@20..48,100..700,0,1');

:root {
  --bg-primary: #F5F3EE;
  --bg-card: #FFFFFF;
  --text-primary: #111827;
  --text-secondary: #6B7280;
  --text-muted: #9CA3AF;
  --accent: #E85D2A;
  --accent-hover: #D9481C;
  --accent-light: #FEF3EC;
  --border: #E5E2DC;
  --border-light: #ECE7E1;
  --success: #10B981;
  --warning: #F59E0B;
  --danger: #EF4444;
  --info: #3B82F6;
  --radius-card: 16px;
  --radius-button: 10px;
  --radius-input: 10px;
}

html, body, * {
  font-family: 'Geist', -apple-system, BlinkMacSystemFont, sans-serif !important;
}

.stApp {
  background-color: var(--bg-primary);
}

.stApp > header {
  background-color: var(--bg-primary) !important;
  height: 0 !important;
  display: none !important;
}

.block-container {
  padding-top: 2.5rem !important;
  padding-bottom: 2rem !important;
}

h1 {
  font-size: 1.75rem;
  font-weight: 700;
  letter-spacing: -0.025em;
  color: var(--text-primary);
}

h2 {
  font-size: 1.2rem;
  font-weight: 600;
  letter-spacing: -0.02em;
  color: var(--text-primary);
  margin-bottom: 1rem;
}

h3 {
  font-size: 1.05rem;
  font-weight: 600;
  color: var(--text-primary);
}

p, .stMarkdown p, li {
  color: var(--text-secondary);
  line-height: 1.6;
}

.stCaption, .caption {
  color: var(--text-muted);
  font-size: 0.85rem;
}

.stTextInput > div > div, .stSelectbox > div > div,
.stTextArea > div > div {
  background-color: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: var(--radius-input);
  color: var(--text-primary);
}

.stTextInput > div > div:focus-within,
.stSelectbox > div > div:focus-within,
.stTextArea > div > div:focus-within {
  border-color: var(--accent);
  box-shadow: 0 0 0 2px var(--accent-light);
}

.stCheckbox label, .stSlider label {
  color: var(--text-secondary);
}

.stButton > button {
  background-color: var(--accent);
  color: white;
  border: none;
  border-radius: var(--radius-button);
  font-weight: 500;
  font-size: 0.9rem;
  padding: 0.4rem 1.2rem;
  transition: background-color 0.15s ease;
}

.stButton > button:hover {
  background-color: var(--accent-hover);
  color: white;
  border: none;
}

button[kind="primary"],
button[kind="primaryFormSubmit"] {
  color: white !important;
}

.stButton > button[kind="secondary"] {
  background-color: transparent;
  color: var(--text-primary);
  border: 1px solid var(--border);
}

.stButton > button[kind="secondary"]:hover {
  background-color: var(--border-light);
  border-color: var(--text-muted);
}

.stAlert {
  border-radius: 8px;
  border: none;
}

.stProgress > div > div {
  background-color: var(--accent);
}

.stSpinner > div {
  border-color: var(--accent) !important;
}

.stTabs button {
  color: var(--text-secondary);
  font-weight: 500;
}

.stTabs button[aria-selected="true"] {
  color: var(--accent);
  border-bottom-color: var(--accent);
}

.stExpander {
  background-color: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: 8px;
}

.hero-logo {
  display: flex;
  justify-content: center;
  margin: 0.5rem 0 0.15rem;
}

.hero-logo svg {
  width: 360px;
  max-width: 90vw;
  height: auto;
}

.hero-subtitle {
  text-align: center;
  font-size: 0.95rem;
  font-weight: 500;
  color: var(--text-secondary);
  margin: 0.15rem 0 1.5rem;
}

.sidebar-logo {
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 0.75rem 0 0.5rem 0;
}

.sidebar-logo svg {
  width: 120px;
  height: auto;
}

hr {
  border-color: var(--border);
  margin: 1.5rem 0;
}

.stInfo {
  background-color: var(--accent-light);
  border: 1px solid var(--accent);
  border-radius: 8px;
  color: var(--text-primary);
}

.stWarning {
  background-color: #FFFBEB;
  border: 1px solid var(--warning);
  border-radius: 8px;
  color: var(--text-primary);
}

.stSuccess {
  background-color: #F0FDF4;
  border: 1px solid var(--success);
  border-radius: 8px;
  color: var(--text-primary);
}

.stError {
  background-color: #FEF2F2;
  border: 1px solid var(--danger);
  border-radius: 8px;
  color: var(--text-primary);
}'''
