def get_table_css():
    return '''

.stDataFrame {
  border: 1px solid #ECE7E1;
  border-radius: 18px;
  overflow: hidden;
  background: #FFFFFF;
  box-shadow: 0 1px 2px rgba(0,0,0,.03), 0 8px 24px rgba(0,0,0,.04);
}

.stDataFrame table {
  border-collapse: collapse;
  width: 100%;
}

.stDataFrame thead tr th {
  background-color: #F8F6F2;
  color: #6B7280;
  font-size: 13px;
  font-weight: 600;
  letter-spacing: 0.04em;
  text-transform: uppercase;
  border-bottom: 1px solid #ECE7E1;
  padding: 14px 16px;
  text-align: left;
}

.stDataFrame tbody tr td {
  padding: 14px 16px;
  font-size: 14px;
  color: #111827;
  border-bottom: 1px solid #ECE7E1;
}

.stDataFrame tbody tr:last-child td {
  border-bottom: none;
}

.stDataFrame tbody tr:nth-child(even) td {
  background-color: #FCFBF8;
}

.stDataFrame tbody tr:hover td {
  background-color: #F6F2ED;
}

.stDataFrame tbody tr td:first-child {
  font-weight: 600;
  color: #111827;
}

'''

