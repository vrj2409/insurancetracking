import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import json

# ── Constants ─────────────────────────────────────────────────────────────────
SHEET_ID   = "1V5Jb_-EOSsWlyuj5GcBYaZTrIsbDp7T_xVyEWTGv064"
SHEET_NAME = "Sheet1"
SCOPES = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive",
]

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Insurance Dashboard",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CSS ────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
:root{
  --bg:#0a0e1a;--panel:#111827;--card:#1f2937;--border:#374151;
  --blue:#3b82f6;--cyan:#06b6d4;--green:#10b981;--red:#ef4444;--amber:#f59e0b;
  --text:#f9fafb;--muted:#9ca3af;
}
html,body,[class*="css"],.stApp{background:var(--bg);color:var(--text);font-family:'Inter',sans-serif;}
#MainMenu,footer,header{visibility:hidden;}
.block-container{padding:2rem 3rem;max-width:1400px;}
section[data-testid="stSidebar"]{background:var(--panel)!important;border-right:1px solid var(--border);padding:1.5rem 1rem;}
section[data-testid="stSidebar"] *{color:var(--text)!important;}
section[data-testid="stSidebar"] label{font-size:.75rem!important;font-weight:500;
  text-transform:uppercase;color:var(--muted)!important;letter-spacing:.05em;}
.kpi{background:var(--card);border:1px solid var(--border);border-radius:12px;
  padding:1.5rem;position:relative;overflow:hidden;transition:all .3s ease;box-shadow:0 1px 3px rgba(0,0,0,.2);}
.kpi:hover{transform:translateY(-2px);box-shadow:0 8px 24px rgba(59,130,246,.15);}
.kpi::before{content:'';position:absolute;top:0;left:0;right:0;height:3px;}
.kpi-total::before{background:linear-gradient(90deg,var(--blue),var(--cyan));}
.kpi-valid::before{background:var(--green);}
.kpi-invalid::before{background:var(--red);}
.kpi-review::before{background:var(--amber);}
.kpi-money::before{background:linear-gradient(90deg,var(--cyan),#8b5cf6);}
.kpi-label{font-size:.7rem;font-weight:600;letter-spacing:.08em;
  text-transform:uppercase;color:var(--muted);margin-bottom:.5rem;}
.kpi-val{font-size:2rem;font-weight:700;color:var(--text);line-height:1.2;}
.kpi-sub{font-size:.75rem;color:var(--muted);margin-top:.4rem;}
.sec{font-size:.7rem;font-weight:600;letter-spacing:.08em;text-transform:uppercase;
  color:var(--muted);border-left:3px solid var(--blue);padding-left:.75rem;margin:1.5rem 0 1rem;}
.stButton>button{background:var(--blue)!important;color:white!important;border:none!important;
  border-radius:8px!important;font-size:.85rem!important;font-weight:500!important;
  padding:.6rem 1.2rem!important;width:100%;transition:all .2s!important;}
.stButton>button:hover{background:#2563eb!important;transform:translateY(-1px)!important;}
.stDownloadButton>button{background:var(--card)!important;border:1px solid var(--border)!important;
  color:var(--text)!important;border-radius:8px!important;font-size:.85rem!important;font-weight:500!important;}
.stDownloadButton>button:hover{border-color:var(--blue)!important;background:rgba(59,130,246,.1)!important;}
div[data-testid="stFileUploader"]{background:var(--card);border:1px solid var(--border);border-radius:8px;padding:1rem;}
div[data-testid="stFileUploader"] label{font-size:.75rem!important;font-weight:500!important;}
</style>
""", unsafe_allow_html=True)


# ── Data helpers ───────────────────────────────────────────────────────────────
@st.cache_data(ttl=300, show_spinner=False)
def fetch_sheet(creds_json_str: str) -> pd.DataFrame:
    import gspread
    from google.oauth2.service_account import Credentials
    creds_dict = json.loads(creds_json_str)
    creds = Credentials.from_service_account_info(creds_dict, scopes=SCOPES)
    gc = gspread.authorize(creds)
    ws = gc.open_by_key(SHEET_ID).worksheet(SHEET_NAME)
    return pd.DataFrame(ws.get_all_records())

def sample_data() -> pd.DataFrame:
    return pd.DataFrame([
        {"job_id":"JOB_001","claim_id":"CLM_1001","policy_number":"PLCY_77891","processing_status":"Completed",
         "validation_status":"Valid","validation_reason":"Incident date within policy period",
         "coverage_type":"Motor","covered_events":"Accident, Collision","excluded_events":"Wear and Tear",
         "policy_start_date":"01-01-2024","policy_end_date":"31-12-2024","waiting_period":0,
         "policy_limit_amount":200000,"incident_date":"15-03-2024","incident_description":"Rear-end collision",
         "incident_cause":"Collision","incident_location":"Chennai","claim_reported_date":"16-03-2024","claimed_amount":45000},
        {"job_id":"JOB_002","claim_id":"CLM_1002","policy_number":"PLCY_88213","processing_status":"Completed",
         "validation_status":"Invalid","validation_reason":"Incident cause matches excluded event",
         "coverage_type":"Property","covered_events":"Fire, Theft, Storm","excluded_events":"Flood, War",
         "policy_start_date":"01-01-2024","policy_end_date":"31-12-2024","waiting_period":0,
         "policy_limit_amount":500000,"incident_date":"20-05-2024","incident_description":"Water damage due to Flood",
         "incident_cause":"Flood","incident_location":"Mumbai","claim_reported_date":"21-05-2024","claimed_amount":120000},
        {"job_id":"JOB_003","claim_id":"CLM_1003","policy_number":"PLCY_99122","processing_status":"Completed",
         "validation_status":"Needs Review","validation_reason":"Claimed amount exceeds policy limit",
         "coverage_type":"Health","covered_events":"Hospitalization","excluded_events":"Cosmetic Treatment",
         "policy_start_date":"01-01-2024","policy_end_date":"31-12-2024","waiting_period":30,
         "policy_limit_amount":100000,"incident_date":"10-02-2024","incident_description":"Knee surgery",
         "incident_cause":"Accident Injury","incident_location":"Bangalore","claim_reported_date":"11-02-2024","claimed_amount":150000},
        {"job_id":"JOB_004","claim_id":"CLM_1004","policy_number":"PLCY_66554","processing_status":"Completed",
         "validation_status":"Invalid","validation_reason":"Incident date outside policy period",
         "coverage_type":"Motor","covered_events":"Accident, Theft","excluded_events":"Racing, Intentional",
         "policy_start_date":"01-01-2023","policy_end_date":"31-12-2023","waiting_period":0,
         "policy_limit_amount":300000,"incident_date":"15-01-2024","incident_description":"Vehicle hit while parked",
         "incident_cause":"Collision","incident_location":"Delhi","claim_reported_date":"16-01-2024","claimed_amount":35000},
        {"job_id":"JOB_005","claim_id":"CLM_1005","policy_number":"PLCY_77432","processing_status":"Completed",
         "validation_status":"Valid","validation_reason":"Covered event and all conditions met",
         "coverage_type":"Travel","covered_events":"Medical Emergency","excluded_events":"Self-inflicted Injury",
         "policy_start_date":"01-06-2024","policy_end_date":"31-05-2025","waiting_period":0,
         "policy_limit_amount":250000,"incident_date":"10-09-2024","incident_description":"Medical treatment abroad",
         "incident_cause":"Medical Emergency","incident_location":"Dubai","claim_reported_date":"11-09-2024","claimed_amount":60000},
        {"job_id":"JOB_006","claim_id":"CLM_99232","policy_number":"POL_784512","processing_status":"Completed",
         "validation_status":"Valid","validation_reason":"The incident cause is covered",
         "coverage_type":"Property Damage","covered_events":"Fire, Theft, Accidental damage",
         "excluded_events":"Flood, Natural calamity, War and terrorism",
         "policy_start_date":"01-01-2024","policy_end_date":"","waiting_period":0,
         "policy_limit_amount":500000,"incident_date":"10-09-2024","incident_description":"Electrical short circuit",
         "incident_cause":"Electrical short circuit","incident_location":"Chennai, Tamil Nadu",
         "claim_reported_date":"12-09-2024","claimed_amount":85000},
    ])

def clean_df(df: pd.DataFrame) -> pd.DataFrame:
    df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]
    for col in ["claimed_amount","policy_limit_amount","waiting_period"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)
    return df


# ── Session state ──────────────────────────────────────────────────────────────
if "df_raw"    not in st.session_state: st.session_state.df_raw    = None
if "connected" not in st.session_state: st.session_state.connected = False


# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style='padding:.5rem 0 1.5rem;border-bottom:1px solid var(--border);margin-bottom:1.5rem'>
      <div style='font-size:1.1rem;font-weight:700;color:var(--text);letter-spacing:.02em'>🛡️ Genesis Insurance</div>
      <div style='font-size:.7rem;color:var(--muted);margin-top:.3rem'>Claims Intelligence Platform</div>
    </div>""", unsafe_allow_html=True)

    st.markdown('<div class="sec">Data Source</div>', unsafe_allow_html=True)
    
    with st.expander("📋 Sheet Configuration", expanded=False):
        st.markdown(f"""
        <div style='background:var(--card);border:1px solid var(--border);border-radius:6px;padding:.75rem;margin-bottom:.75rem;'>
          <div style='font-size:.65rem;color:var(--muted);text-transform:uppercase;letter-spacing:.05em;margin-bottom:.3rem'>Sheet ID</div>
          <div style='font-size:.7rem;color:var(--blue);word-break:break-all;font-family:monospace'>{SHEET_ID}</div>
        </div>""", unsafe_allow_html=True)
        st.info("⚠️ Make sure to share the Google Sheet with the service account email (found in your JSON file)")
        st.markdown("**Steps:**\n1. Open your Google Sheet\n2. Click 'Share'\n3. Add the `client_email` from your JSON\n4. Give it 'Viewer' or 'Editor' access")

    cred_file = st.file_uploader("📁 Service Account JSON", type=["json"], label_visibility="visible")

    if cred_file:
        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            if st.button("🔌 Connect", use_container_width=True):
                try:
                    # Read file content once
                    cred_file.seek(0)  # Reset file pointer
                    file_content = cred_file.read()
                    
                    # Decode if bytes
                    if isinstance(file_content, bytes):
                        creds_str = file_content.decode("utf-8")
                    else:
                        creds_str = file_content
                    
                    # Validate JSON
                    creds_dict = json.loads(creds_str)
                    
                    # Verify required fields
                    required_fields = ["type", "project_id", "private_key", "client_email"]
                    missing = [f for f in required_fields if f not in creds_dict]
                    if missing:
                        st.error(f"❌ Missing fields in JSON: {', '.join(missing)}")
                    else:
                        # Connect to sheet
                        with st.spinner("Connecting to Google Sheets..."):
                            df_fetched = fetch_sheet(creds_str)
                        
                        st.session_state.df_raw = clean_df(df_fetched)
                        st.session_state.connected = True
                        st.success(f"✅ {len(st.session_state.df_raw)} rows loaded")
                        st.rerun()
                except json.JSONDecodeError as e:
                    st.error(f"❌ Invalid JSON file: {str(e)}")
                except ImportError as e:
                    st.error(f"❌ Missing library: {str(e)}\n\nRun: pip install gspread google-auth")
                except Exception as e:
                    st.error(f"❌ Connection failed:\n\n{str(e)}")
                    with st.expander("Show full error"):
                        st.code(str(e))
        
        with col_btn2:
            if st.session_state.connected and st.button("🔄 Refresh", use_container_width=True):
                st.cache_data.clear()
                st.session_state.df_raw = None
                st.session_state.connected = False
                st.rerun()
    else:
        st.info("💡 Upload credentials to connect live data. Demo data shown below.")

    if st.session_state.connected:
        st.success("🟢 Connected to live sheet")

    st.markdown('<div style="margin:1.5rem 0;border-top:1px solid var(--border)"></div>', unsafe_allow_html=True)

    # ── Filters ──
    base = st.session_state.df_raw if st.session_state.df_raw is not None else clean_df(sample_data())

    st.markdown('<div class="sec">Filters</div>', unsafe_allow_html=True)
    status_opts = ["All"] + sorted(base["validation_status"].dropna().unique().tolist())
    sel_status = st.selectbox("Validation Status", status_opts, key="status_filter")

    cov_opts = sorted(base["coverage_type"].dropna().unique().tolist()) if "coverage_type" in base.columns else []
    sel_cov = st.multiselect("Coverage Type", cov_opts, default=cov_opts, key="cov_filter")

    loc_opts = sorted(base["incident_location"].dropna().unique().tolist()) if "incident_location" in base.columns else []
    sel_loc = st.multiselect("Location", loc_opts, default=loc_opts, key="loc_filter")

    st.markdown('<div style="margin:1.5rem 0;border-top:1px solid var(--border)"></div>', unsafe_allow_html=True)
    st.markdown(f'<div style="font-size:.65rem;color:var(--muted);text-align:center">Last updated: {datetime.now().strftime("%H:%M:%S")}</div>', unsafe_allow_html=True)


# ── Load & apply filters ───────────────────────────────────────────────────────
df_all = st.session_state.df_raw if st.session_state.df_raw is not None else clean_df(sample_data())
df = df_all.copy()
if sel_status != "All":               df = df[df["validation_status"] == sel_status]
if sel_cov and "coverage_type"        in df.columns: df = df[df["coverage_type"].isin(sel_cov)]
if sel_loc  and "incident_location"   in df.columns: df = df[df["incident_location"].isin(sel_loc)]


# ── Header ─────────────────────────────────────────────────────────────────────
badge = ('<span style="background:rgba(16,185,129,.1);border:1px solid var(--green);color:var(--green);border-radius:20px;padding:.25rem .75rem;font-size:.7rem;font-weight:600">● LIVE</span>'
         if st.session_state.connected else
         '<span style="background:rgba(156,163,175,.1);border:1px solid var(--muted);color:var(--muted);border-radius:20px;padding:.25rem .75rem;font-size:.7rem;font-weight:600">◌ DEMO</span>')
st.markdown(f"""
<div style='display:flex;align-items:center;gap:1rem;margin-bottom:2rem;padding-bottom:1rem;border-bottom:1px solid var(--border)'>
  <div style='font-size:1.75rem;font-weight:700;color:var(--text)'>Insurance Claims Dashboard</div>
  {badge}
  <div style='flex:1'></div>
  <div style='font-size:.8rem;color:var(--muted);font-weight:500'>{len(df)} of {len(df_all)} claims</div>
</div>""", unsafe_allow_html=True)


# ── KPIs ───────────────────────────────────────────────────────────────────────
total    = len(df)
valid    = int((df["validation_status"] == "Valid").sum())
invalid  = int((df["validation_status"] == "Invalid").sum())
review   = int((df["validation_status"] == "Needs Review").sum())
exposure = float(df["claimed_amount"].sum()) if "claimed_amount" in df.columns else 0.0
pct = lambda n: f"{round(n/total*100)}%" if total else "—"
inr = lambda v: f"₹{v/100000:.1f}L" if v >= 100000 else f"₹{v:,.0f}"

c1,c2,c3,c4,c5 = st.columns(5)
for col,cls,lbl,val,sub in [
    (c1,"total",  "Total Claims",      str(total),    f"{len(df_all)} in dataset"),
    (c2,"valid",  "Valid",             str(valid),    pct(valid)),
    (c3,"invalid","Invalid",           str(invalid),  pct(invalid)),
    (c4,"review", "Needs Review",      str(review),   pct(review)),
    (c5,"money",  "Financial Exposure",inr(exposure), "total claimed"),
]:
    with col:
        st.markdown(f'<div class="kpi kpi-{cls}"><div class="kpi-label">{lbl}</div><div class="kpi-val">{val}</div><div class="kpi-sub">{sub}</div></div>', unsafe_allow_html=True)

st.markdown("<div style='height:1.5rem'></div>", unsafe_allow_html=True)


# ── Charts ─────────────────────────────────────────────────────────────────────
cc1, cc2 = st.columns([3, 2], gap="large")

with cc1:
    st.markdown('<div class="sec">Financial Exposure by Claim</div>', unsafe_allow_html=True)
    if not df.empty and "claimed_amount" in df.columns:
        ds = df.sort_values("claimed_amount", ascending=False)
        cmap = {"Valid":"#10b981","Invalid":"#ef4444","Needs Review":"#f59e0b"}
        fig = go.Figure(go.Bar(
            x=ds["claim_id"], y=ds["claimed_amount"],
            marker=dict(color=ds["validation_status"].map(cmap).fillna("#3b82f6").tolist(), line_width=0),
            customdata=ds[["policy_number","validation_status","incident_cause"]].values,
            hovertemplate="<b>%{x}</b><br>Policy: %{customdata[0]}<br>Cause: %{customdata[2]}<br>₹%{y:,.0f} · %{customdata[1]}<extra></extra>",
        ))
        fig.update_layout(paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",
            font=dict(family="Inter",color="#9ca3af",size=11),
            margin=dict(l=0,r=0,t=10,b=0),height=260,bargap=0.3,
            xaxis=dict(showgrid=False,tickfont=dict(size=10)),
            yaxis=dict(showgrid=True,gridcolor="#374151",tickformat=",.0f",tickfont=dict(size=10)))
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar":False})

with cc2:
    st.markdown('<div class="sec">Claims Distribution</div>', unsafe_allow_html=True)
    counts = df["validation_status"].value_counts()
    if not counts.empty:
        cmap2 = {"Valid":"#10b981","Invalid":"#ef4444","Needs Review":"#f59e0b"}
        fig2  = go.Figure(go.Pie(
            labels=counts.index, values=counts.values, hole=0.58,
            marker=dict(colors=[cmap2.get(s,"#3b82f6") for s in counts.index],
                        line=dict(color="#0a0e1a",width=3)),
            textfont=dict(family="Inter",size=11),
            hovertemplate="<b>%{label}</b><br>%{value} · %{percent}<extra></extra>",
        ))
        fig2.update_layout(paper_bgcolor="rgba(0,0,0,0)",
            font=dict(family="Inter",color="#9ca3af"),
            margin=dict(l=0,r=0,t=10,b=0),height=260,
            legend=dict(font=dict(color="#9ca3af",size=10),bgcolor="rgba(0,0,0,0)",x=1.02,y=0.5),
            annotations=[dict(text=f"<b>{total}</b>",x=0.5,y=0.5,
                font=dict(size=20,color="#f9fafb",family="Inter"),showarrow=False)])
        st.plotly_chart(fig2, use_container_width=True, config={"displayModeBar":False})

# Coverage bar
if "coverage_type" in df.columns and df["coverage_type"].nunique() > 1:
    st.markdown('<div class="sec" style="margin-top:8px">Exposure by Coverage Type</div>', unsafe_allow_html=True)
    cov = df.groupby("coverage_type").agg(claims=("claim_id","count"),exposure=("claimed_amount","sum")).reset_index().sort_values("exposure",ascending=True)
    fig3 = go.Figure(go.Bar(
        y=cov["coverage_type"], x=cov["exposure"], orientation="h",
        marker=dict(color=cov["exposure"],colorscale=[[0,"#1e3a8a"],[0.5,"#3b82f6"],[1,"#06b6d4"]],line_width=0),
        text=cov.apply(lambda r: f"₹{r['exposure']:,.0f}  ({r['claims']} claims)",axis=1),
        textposition="outside",textfont=dict(color="#9ca3af",size=10,family="Inter"),
        hovertemplate="<b>%{y}</b><br>₹%{x:,.0f}<extra></extra>",
    ))
    fig3.update_layout(paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter",color="#9ca3af",size=11),
        margin=dict(l=0,r=200,t=10,b=0),height=max(200,len(cov)*45),
        xaxis=dict(showgrid=True,gridcolor="#374151",tickformat=",.0f"),
        yaxis=dict(showgrid=False))
    st.plotly_chart(fig3, use_container_width=True, config={"displayModeBar":False})


# ── Table ──────────────────────────────────────────────────────────────────────
st.markdown('<div class="sec" style="margin-top:8px">Claims Detail</div>', unsafe_allow_html=True)
TABLE_COLS = [c for c in ["claim_id","policy_number","coverage_type","incident_date",
    "incident_cause","incident_location","claimed_amount","validation_status","validation_reason"] if c in df.columns]
df_tbl = df[TABLE_COLS].copy()
if "claimed_amount" in df_tbl.columns:
    df_tbl["claimed_amount"] = df_tbl["claimed_amount"].apply(lambda x: f"₹{int(x):,}" if pd.notna(x) and x != 0 else "—")

def hl(val):
    if val=="Valid":        return "color:#10b981;font-weight:600"
    if val=="Invalid":      return "color:#ef4444;font-weight:600"
    if val=="Needs Review": return "color:#f59e0b;font-weight:600"
    return ""

styled = (df_tbl.style
    .applymap(hl, subset=["validation_status"] if "validation_status" in df_tbl.columns else [])
    .set_properties(**{"background-color":"#1f2937","color":"#f9fafb","border-color":"#374151",
                       "font-family":"Inter, sans-serif","font-size":"0.8rem"})
    .set_table_styles([{"selector":"th","props":[("background-color","#111827"),("color","#9ca3af"),
        ("font-family","Inter, sans-serif"),("font-size","0.7rem"),("letter-spacing","0.05em"),
        ("text-transform","uppercase"),("font-weight","600"),("border-bottom","1px solid #374151")]}]))
st.dataframe(styled, use_container_width=True, height=min(420,(len(df_tbl)+1)*38+6), hide_index=True)


# ── Export ─────────────────────────────────────────────────────────────────────
st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)
b1,b2,_ = st.columns([1,1,6])
with b1:
    st.download_button("⬇ Export CSV", df.to_csv(index=False).encode(),
        f"claims_{datetime.now().strftime('%Y%m%d_%H%M')}.csv","text/csv",use_container_width=True)
with b2:
    if st.button("🔄 Refresh Data", use_container_width=True):
        st.cache_data.clear()
        st.session_state.df_raw = None
        st.session_state.connected = False
        st.rerun()
