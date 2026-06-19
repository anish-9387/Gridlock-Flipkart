def get_table_css():
    return '''

.stDataFrame {
  border: 1px solid var(--border-light);
  border-radius: 18px;
  overflow: hidden;
  background: var(--bg-card);
  box-shadow: 0 1px 2px rgba(0,0,0,.03), 0 8px 24px rgba(0,0,0,.04);
}

.stDataFrame table {
  border-collapse: collapse;
  width: 100%;
}

.stDataFrame thead tr th {
  background-color: var(--bg-subtle);
  color: var(--text-secondary);
  font-size: 13px;
  font-weight: 600;
  letter-spacing: 0.04em;
  text-transform: uppercase;
  border-bottom: 1px solid var(--border-light);
  padding: 14px 16px;
  text-align: left;
}

.stDataFrame tbody tr td {
  padding: 14px 16px;
  font-size: 14px;
  color: var(--text-primary);
  border-bottom: 1px solid var(--border-light);
}

.stDataFrame tbody tr:last-child td {
  border-bottom: none;
}

.stDataFrame tbody tr:nth-child(even) td {
  background-color: var(--bg-row-even);
}

.stDataFrame tbody tr:hover td {
  background-color: var(--bg-row-hover);
}

.stDataFrame tbody tr td:first-child {
  font-weight: 600;
  color: var(--text-primary);
}

'''

