"""
app.py — DataMind AI Agent v5
Fix: Result session_state mein store — dropdown change pe page jump bilkul nahi
"""

import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
import os
import io
import html as html_module

st.set_page_config(
    page_title="Data Analyst Agent",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

try:
    from setup_db import create_database
    from sql_agent import create_sql_agent
except ImportError as e:
    st.error(
        "**Import error:** `" + str(e).replace("`", "'") + "`\n\n"
        "Terminal mein `sql_ai_agent` folder mein jao aur chalao:\n"
        "`python -m pip install -r requirements.txt`\n\nPhir: `streamlit run app.py`"
    )
    st.stop()

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
.app-header {
    display: flex; align-items: center; justify-content: space-between;
    padding: 18px 28px;
    background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
    border-radius: 16px; margin-bottom: 24px;
    box-shadow: 0 8px 32px rgba(102,126,234,0.25);
}
.app-name {
    font-size: 2rem; font-weight: 900;
    background: linear-gradient(90deg, #a78bfa, #60a5fa, #f472b6);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    letter-spacing: -0.5px;
}
.app-tagline { color: #94a3b8; font-size: 0.88rem; margin-top: 2px; }
.user-welcome { text-align: right; }
.user-label { color: #94a3b8; font-size: 0.78rem; text-transform: uppercase; letter-spacing: 1px; }
.user-name-display { font-size: 1.15rem; font-weight: 700; color: #a78bfa; }

.answer-box {
    background: #1e1b4b; border: 1px solid #4c1d95;
    padding: 18px 22px; border-radius: 12px;
    border-left: 5px solid #7c3aed;
    font-size: 1.05rem; color: #e2e8f0 !important; line-height: 1.7;
}
.sql-box {
    background: #0d1117; color: #79c0ff;
    padding: 14px 18px; border-radius: 10px;
    font-family: 'Courier New', monospace; font-size: 0.88rem;
    border-left: 4px solid #388bfd; white-space: pre-wrap;
}
.stButton > button {
    background: linear-gradient(135deg, #7c3aed, #2563eb);
    color: white !important; border: none; border-radius: 10px;
    padding: 0.65rem 2rem; font-size: 1rem; font-weight: 700; width: 100%;
}
.stButton > button:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(124,58,237,0.45);
}
.footer {
    margin-top: 48px; padding: 20px;
    background: linear-gradient(135deg, #0f0c29, #1e1b4b);
    border-radius: 12px; text-align: center; border-top: 2px solid #4c1d95;
}
.footer-built { color: #64748b; font-size: 0.8rem; margin-bottom: 4px; }
.footer-name {
    font-size: 1.1rem; font-weight: 800;
    background: linear-gradient(90deg, #a78bfa, #60a5fa);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
}
.footer-title { color: #94a3b8; font-size: 0.82rem; margin-top: 2px; }
.upload-hint {
    background: #1e1b4b; border: 2px dashed #4c1d95;
    border-radius: 12px; padding: 14px;
    text-align: center; color: #94a3b8; font-size: 0.85rem;
}
[data-testid="metric-container"] {
    background: #1e1b4b; border: 1px solid #312e81;
    border-radius: 12px; padding: 12px 16px;
}
</style>
""", unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════
# HELPERS
# ════════════════════════════════════════════════════════════
def file_to_sqlite(uploaded_file):
    fname = uploaded_file.name.lower()
    if fname.endswith((".xlsx", ".xls", ".xlsm")):
        engine = "openpyxl" if not fname.endswith(".xls") else "xlrd"
        df = pd.read_excel(uploaded_file, engine=engine)
    else:
        raw = uploaded_file.read()
        df = None
        for enc in ("utf-8", "utf-8-sig", "latin-1", "cp1252"):
            try:
                df = pd.read_csv(io.StringIO(raw.decode(enc)))
                break
            except Exception:
                continue
        if df is None:
            raise ValueError("CSV encoding detect nahi hua")

    df.columns = [
        c.strip().lower().replace(" ", "_").replace("-", "_")
         .replace("(", "").replace(")", "")
        for c in df.columns
    ]
    db_path, table_name = "user_upload.db", "user_data"
    conn = sqlite3.connect(db_path)
    df.to_sql(table_name, conn, if_exists="replace", index=False)
    conn.close()
    return db_path, table_name, df


def load_table_df(table, db="business.db"):
    conn = sqlite3.connect(db)
    df   = pd.read_sql_query(f"SELECT * FROM {table}", conn)
    conn.close()
    return df


@st.cache_resource(show_spinner=False)
def init_default_agent():
    if not os.path.exists("business.db"):
        create_database()
    return create_sql_agent()


def build_agent_title(user_name):
    n = (user_name or "").strip()
    if not n:
        return "My Data Analyst Agent"
    first = n.split()[0]
    first = (first[:1].upper() + first[1:].lower()) if len(first) > 1 else first.upper()
    return f"{first} Data Analyst Agent"


# ── Chart setup ───────────────────────────────────────────────────────────────
_QUAL   = px.colors.qualitative.Bold + px.colors.qualitative.Dark24
_CSCALE = [[0.0,"#312e81"],[0.4,"#7c3aed"],[0.7,"#c026d3"],[1.0,"#f97316"]]

CHART_OPTIONS = {
    "📊 Vertical Bars":   "bar_v",
    "📶 Horizontal Bars": "bar_h",
    "📈 Line / Trend":    "line",
    "🥧 Pie Chart":       "pie",
    "🌊 Area Chart":      "area",
    "🔮 Scatter Plot":    "scatter",
    "📉 Histogram":       "histogram",
}

def _cols(df):
    return (
        df.select_dtypes(include="number").columns.tolist(),
        df.select_dtypes(exclude="number").columns.tolist(),
    )

def _base_layout(fig):
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(15,23,42,0.85)",
        font=dict(color="#e2e8f0", family="Segoe UI, system-ui", size=13),
        margin=dict(l=12, r=12, t=44, b=12),
        hovermode="closest",
        hoverlabel=dict(bgcolor="#1e1b4b", font_size=13,
                        font_color="#f8fafc", bordercolor="#7c3aed"),
        xaxis=dict(gridcolor="rgba(99,102,241,0.25)", zeroline=False,
                   tickfont=dict(color="#cbd5e1")),
        yaxis=dict(gridcolor="rgba(99,102,241,0.2)", zeroline=False,
                   tickfont=dict(color="#cbd5e1")),
        coloraxis_showscale=False,
        showlegend=False,
    )

def make_chart(df, kind):
    if df is None or df.empty:
        return None
    num_cols, cat_cols = _cols(df)
    if not num_cols:
        return None
    fig = None

    if kind == "bar_v" and cat_cols:
        dfs = df.sort_values(by=num_cols[0], ascending=False).head(20)
        fig = px.bar(dfs, x=cat_cols[0], y=num_cols[0], color=num_cols[0],
                     color_continuous_scale=_CSCALE, text=num_cols[0])
        fig.update_traces(texttemplate="%{text:,.1f}", textposition="outside",
                          textfont_color="#f1f5f9",
                          hovertemplate="<b>%{x}</b><br>%{y:,.2f}<extra></extra>")
        fig.update_layout(xaxis_tickangle=-35, coloraxis_showscale=True)

    elif kind == "bar_h" and cat_cols:
        dfs = df.sort_values(by=num_cols[0], ascending=True).tail(20)
        fig = px.bar(dfs, x=num_cols[0], y=cat_cols[0], orientation="h",
                     color=num_cols[0], color_continuous_scale=_CSCALE, text=num_cols[0])
        fig.update_traces(texttemplate="%{text:,.1f}", textposition="outside",
                          textfont_color="#f1f5f9",
                          hovertemplate="<b>%{y}</b><br>%{x:,.2f}<extra></extra>")
        fig.update_layout(coloraxis_showscale=True)

    elif kind == "line" and cat_cols:
        dfs = df.sort_values(by=cat_cols[0])
        fig = px.line(dfs, x=cat_cols[0], y=num_cols[0], markers=True, line_shape="spline")
        fig.update_traces(line=dict(width=3.5, color="#38bdf8"),
                          marker=dict(size=11, color="#f472b6",
                                      line=dict(width=2, color="#fff")),
                          hovertemplate="<b>%{x}</b><br>%{y:,.2f}<extra></extra>")

    elif kind == "pie" and cat_cols:
        fig = px.pie(df, names=cat_cols[0], values=num_cols[0],
                     color_discrete_sequence=_QUAL, hole=0.42)
        fig.update_traces(textposition="inside", textinfo="percent+label", pull=0.025,
                          marker=dict(line=dict(color="#0f172a", width=1.5)),
                          hovertemplate="<b>%{label}</b><br>%{value:,.2f}<br>%{percent}<extra></extra>")
        fig.update_layout(showlegend=True,
                          legend=dict(bgcolor="rgba(15,23,42,0.9)",
                                      bordercolor="#4c1d95", borderwidth=1,
                                      font=dict(size=11)))

    elif kind == "area" and cat_cols:
        dfs = df.sort_values(by=cat_cols[0])
        fig = px.area(dfs, x=cat_cols[0], y=num_cols[0])
        fig.update_traces(line=dict(color="#a78bfa", width=2.5),
                          fillcolor="rgba(167,139,250,0.4)",
                          hovertemplate="<b>%{x}</b><br>%{y:,.2f}<extra></extra>")

    elif kind == "scatter" and len(num_cols) >= 2:
        fig = px.scatter(df, x=num_cols[0], y=num_cols[1],
                         color=cat_cols[0] if cat_cols else None,
                         color_discrete_sequence=_QUAL)
        fig.update_traces(marker=dict(size=12, opacity=0.88,
                                      line=dict(width=1.5, color="#0f172a")),
                          hovertemplate="<b>X:</b> %{x:,.2f}<br><b>Y:</b> %{y:,.2f}<extra></extra>")
        fig.update_layout(showlegend=bool(cat_cols))

    elif kind == "histogram":
        nb = min(32, max(8, len(df) // 3))
        fig = px.histogram(df, x=num_cols[0], nbins=nb,
                           color_discrete_sequence=["#7c3aed"])
        fig.update_traces(marker=dict(color="#8b5cf6",
                                      line=dict(color="#c4b5fd", width=1)),
                          hovertemplate="Range: %{x}<br>Count: %{y}<extra></extra>")

    if fig:
        _base_layout(fig)
    return fig


PLOTLY_CFG = {
    "displayModeBar": True, "displaylogo": False, "scrollZoom": True,
    "toImageButtonOptions": {"format": "png", "scale": 2},
    "modeBarButtonsToRemove": ["lasso2d", "select2d"],
}


# ════════════════════════════════════════════════════════════
# SESSION STATE INIT  ← ASLI FIX YAHAN HAI
# ════════════════════════════════════════════════════════════
# Result aur df_res session_state mein store karo
# Takay dropdown change pe ye gayab na ho
if "result"     not in st.session_state: st.session_state.result     = None
if "df_res"     not in st.session_state: st.session_state.df_res     = None
if "active_db"  not in st.session_state: st.session_state.active_db  = "business.db"
if "chart_kind" not in st.session_state: st.session_state.chart_kind = "📊 Vertical Bars"


# ════════════════════════════════════════════════════════════
# SIDEBAR
# ════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("## ⚙️ Settings")

    user_name = st.text_input(
        "👤 Your Name", placeholder="e.g. Ali Usman",
        help="Header par '{First} Data Analyst Agent' dikhega",
    )
    st.markdown("---")

    api_key = st.text_input(
        "🔑 API Key", type="password",
        placeholder="OpenAI: sk-...  |  Groq: gsk_...",
    )
    if api_key:
        k = api_key.strip()
        os.environ["OPENAI_API_KEY"] = k
        if k.startswith("gsk_"):
            os.environ["GROQ_API_KEY"] = k
        st.success("✅ API Key set!")
    else:
        st.warning("⚠️ API key enter karein")

    st.markdown("---")
    st.markdown("### 📂 Data Source")
    data_source = st.radio("", ["🏢 Sample Business Data", "📤 Upload Excel / CSV"],
                           label_visibility="collapsed")

    upload_df = upload_db = upload_table = None

    if data_source == "📤 Upload Excel / CSV":
        st.markdown('<div class="upload-hint">📎 Excel (.xlsx, .xls) ya CSV drag karein</div>',
                    unsafe_allow_html=True)
        uploaded_file = st.file_uploader("", type=["xlsx","xls","xlsm","csv"],
                                         label_visibility="collapsed")
        if uploaded_file:
            with st.spinner("⚙️ Loading..."):
                try:
                    upload_db, upload_table, upload_df = file_to_sqlite(uploaded_file)
                    st.success(f"✅ {len(upload_df):,} rows, {len(upload_df.columns)} cols!")
                except Exception as ex:
                    st.error(f"❌ {ex}")
            if upload_df is not None:
                with st.expander("📋 Columns"):
                    for col in upload_df.columns:
                        st.markdown(f"  • `{col}`")

    st.markdown("---")
    st.markdown("### 💡 Examples")
    examples = [
        "Who are top 5 customers by total spending?",
        "What is total revenue by product category?",
        "Show revenue breakdown by category",
        "How many orders are pending vs completed?",
        "Which product sold the most units?",
        "Show orders from Pakistan customers",
        "Average order value per country?",
        "Which month had the highest sales?",
        "Products with stock below 50?",
    ]
    selected_ex = st.selectbox("Pick:", ["(Select)"] + examples)

    st.markdown("---")
    st.markdown("### 📊 Active Database")
    if data_source == "🏢 Sample Business Data":
        st.markdown("- 👥 12 Global Customers\n- 📦 12 Products\n- 🛒 60 Orders")
    elif upload_df is not None:
        st.markdown(f"- 📄 {len(upload_df):,} rows\n- 📋 {len(upload_df.columns)} cols\n- 🗂️ `user_data`")


# ════════════════════════════════════════════════════════════
# HEADER
# ════════════════════════════════════════════════════════════
display_name = user_name.strip() if user_name and user_name.strip() else "Guest"
agent_title  = build_agent_title(user_name)
st.markdown(f"""
<div class="app-header">
  <div>
    <div class="app-name">{html_module.escape(agent_title)}</div>
    <div class="app-tagline">Plain English se apna data samjhein — koi SQL nahi chahiye</div>
  </div>
  <div class="user-welcome">
    <div class="user-label">Welcome</div>
    <div class="user-name-display">👤 {html_module.escape(display_name)}</div>
  </div>
</div>
""", unsafe_allow_html=True)


# ── Active DB ─────────────────────────────────────────────────────────────────
if data_source == "📤 Upload Excel / CSV" and upload_db:
    active_db = upload_db
    st.info(f"📤 Aapka uploaded data — table: `{upload_table}`")
else:
    active_db = "business.db"
    if not os.path.exists("business.db"):
        create_database()

st.session_state.active_db = active_db


# ── Quick Stats ───────────────────────────────────────────────────────────────
if active_db == "business.db" and os.path.exists("business.db"):
    conn = sqlite3.connect("business.db")
    rev  = pd.read_sql_query("SELECT ROUND(SUM(total_amount),2) FROM orders WHERE status='completed'", conn).iloc[0,0]
    ord_ = pd.read_sql_query("SELECT COUNT(*) FROM orders", conn).iloc[0,0]
    cus_ = pd.read_sql_query("SELECT COUNT(*) FROM customers", conn).iloc[0,0]
    pen_ = pd.read_sql_query("SELECT COUNT(*) FROM orders WHERE status='pending'", conn).iloc[0,0]
    conn.close()
    c1,c2,c3,c4 = st.columns(4)
    c1.metric("💰 Total Revenue", f"${rev:,.2f}")
    c2.metric("🛒 Total Orders",  ord_)
    c3.metric("👥 Customers",     cus_)
    c4.metric("⏳ Pending",       pen_)
elif upload_df is not None:
    num_c = upload_df.select_dtypes(include="number").columns.tolist()
    cols  = st.columns(min(4, len(num_c)+1))
    cols[0].metric("📄 Total Rows", f"{len(upload_df):,}")
    for i,c in enumerate(num_c[:3]):
        cols[i+1].metric(f"Σ {c}", f"{upload_df[c].sum():,.1f}")

st.markdown("---")


# ════════════════════════════════════════════════════════════
# QUESTION INPUT
# ════════════════════════════════════════════════════════════
c1, c2 = st.columns([4, 1])
with c1:
    default_q     = selected_ex if selected_ex != "(Select)" else ""
    user_question = st.text_input(
        "Q", value=default_q,
        placeholder="e.g. Who are top 5 customers by revenue?",
        label_visibility="collapsed",
    )
with c2:
    ask_clicked = st.button("🚀 Ask Agent", use_container_width=True)


# ════════════════════════════════════════════════════════════
# AGENT EXECUTION — result session_state mein save karo
# ════════════════════════════════════════════════════════════
if ask_clicked and user_question:
    if not os.environ.get("OPENAI_API_KEY"):
        st.error("❌ Sidebar mein API Key enter karein.")
    elif data_source == "📤 Upload Excel / CSV" and not upload_db:
        st.error("❌ Pehle Excel/CSV upload karein.")
    else:
        import sql_agent as sa
        sa.DB_PATH = active_db
        agent = init_default_agent()

        with st.spinner("🧠 Agent soch raha hai..."):
            try:
                result = agent.invoke({
                    "question": user_question,
                    "schema": "", "sql_query": "", "results": "",
                    "column_names": [], "final_answer": "", "error": "",
                })
                # ✅ Session state mein save karo
                st.session_state.result = result
                st.session_state.chart_kind = "📊 Vertical Bars"  # reset chart on new question

                # df_res bhi save karo
                if result.get("sql_query") and not result.get("error"):
                    try:
                        conn = sqlite3.connect(active_db)
                        st.session_state.df_res = pd.read_sql_query(result["sql_query"], conn)
                        conn.close()
                    except Exception:
                        st.session_state.df_res = None

            except Exception as e:
                st.error(f"**Error:** `{e}`\n\nAPI key check karein.")
                st.stop()

elif ask_clicked:
    st.warning("⚠️ Pehle koi sawal type karein!")


# ════════════════════════════════════════════════════════════
# RESULTS DISPLAY — session_state se render karo
# Yeh hamesha render hoga — dropdown change pe bhi nahi hatega
# ════════════════════════════════════════════════════════════
result = st.session_state.result
df_res = st.session_state.df_res

if result is not None:

    # ── Answer ───────────────────────────────────────────────────────────────
    st.markdown("### 💬 Answer")
    st.markdown(f'<div class="answer-box">{result["final_answer"]}</div>',
                unsafe_allow_html=True)

    # ── Chart Section ─────────────────────────────────────────────────────────
    if df_res is not None and not df_res.empty:
        num_cols, cat_cols = _cols(df_res)

        if num_cols:
            st.markdown("### 📊 Chart")

            # Dropdown + Chart — ek saath, session_state se
            # Page jump BILKUL nahi kyunke result upar se aa raha hai
            hcol, dcol, _ = st.columns([1.1, 1.6, 3.3])
            with hcol:
                st.markdown("**Chart Type:**")
            with dcol:
                st.session_state.chart_kind = st.selectbox(
                    "chart_sel",
                    list(CHART_OPTIONS.keys()),
                    index=list(CHART_OPTIONS.keys()).index(st.session_state.chart_kind),
                    label_visibility="collapsed",
                    key="chart_dropdown",
                )

            kind = CHART_OPTIONS[st.session_state.chart_kind]
            fig  = make_chart(df_res, kind)

            if fig:
                st.plotly_chart(fig, use_container_width=True, config=PLOTLY_CFG)
                st.caption("🖱️ Zoom: mouse wheel · Pan: drag · Save: toolbar top-right")
            else:
                st.info(
                    f"**{st.session_state.chart_kind}** is data par nahi ban sakta. "
                    "Doosra chart type try karein."
                )

    # ── SQL ───────────────────────────────────────────────────────────────────
    with st.expander("🔍 SQL Query Generated"):
        st.markdown(f'<div class="sql-box">{result["sql_query"]}</div>',
                    unsafe_allow_html=True)

    # ── Raw Table ─────────────────────────────────────────────────────────────
    with st.expander("📊 Raw Data Table"):
        if df_res is not None:
            st.dataframe(df_res, use_container_width=True)
            st.download_button(
                "⬇️ Download as CSV",
                df_res.to_csv(index=False),
                "results.csv", "text/csv",
            )
        else:
            st.text(result.get("results", "Data unavailable"))


# ════════════════════════════════════════════════════════════
# DATABASE EXPLORER
# ════════════════════════════════════════════════════════════
st.markdown("---")
st.markdown("### 🗄️ Data Explorer")

if data_source == "🏢 Sample Business Data" and os.path.exists("business.db"):
    t1, t2, t3 = st.tabs(["👥 Customers", "📦 Products", "🛒 Orders"])
    with t1: st.dataframe(load_table_df("customers"), use_container_width=True)
    with t2: st.dataframe(load_table_df("products"),  use_container_width=True)
    with t3: st.dataframe(load_table_df("orders"),    use_container_width=True)
elif upload_df is not None:
    st.markdown(f"**Aapka data** — {len(upload_df):,} rows")
    st.dataframe(upload_df, use_container_width=True)
    buf = io.BytesIO()
    upload_df.to_excel(buf, index=False, engine="openpyxl")
    st.download_button(
        "⬇️ Download as Excel", buf.getvalue(), "your_data.xlsx",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
else:
    st.info("📤 Sidebar se Excel/CSV upload karein ya Sample Data select karein.")


# ════════════════════════════════════════════════════════════
# FOOTER
# ════════════════════════════════════════════════════════════
st.markdown("""
<div class="footer">
    <div class="footer-built">🛠️ Designed & Developed by</div>
    <div class="footer-name">Muhammad Arfan Wazeer</div>
    <div class="footer-title">AI Automation Engineer &nbsp;|&nbsp; LangGraph &nbsp;•&nbsp; n8n &nbsp;•&nbsp; Python &nbsp;•&nbsp; Power BI</div>
    <div style="margin-top:10px; color:#475569; font-size:0.75rem;">
        DataMind AI Agent v5.0 &nbsp;•&nbsp; Built with LangGraph + OpenAI + Streamlit
    </div>
</div>
""", unsafe_allow_html=True)