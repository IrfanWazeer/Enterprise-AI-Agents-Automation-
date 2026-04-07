"""
sql_agent.py — LangGraph SQL AI Agent (Core Logic)

Flow:
  User Question → Get DB Schema → Generate SQL → Execute SQL → Format Answer

Yeh agent:
  1. Database ka structure khud samajhta hai
  2. English sawal ko SQL mein convert karta hai
  3. SQL run karta hai
  4. Result ko simple English mein explain karta hai
"""

import sqlite3
import os
from typing import TypedDict
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.language_models.chat_models import BaseChatModel

DB_PATH = "business.db"

# Groq: gsk_...  |  OpenAI: sk-... / sk-proj-...
_GROQ_MODEL = "llama-3.3-70b-versatile"
_OPENAI_MODEL = "gpt-4o-mini"


def _make_llm() -> BaseChatModel:
    key = (os.environ.get("OPENAI_API_KEY") or os.environ.get("GROQ_API_KEY") or "").strip()
    if not key:
        raise ValueError("API key missing — set it in the app sidebar.")
    if key.startswith("gsk_"):
        from langchain_groq import ChatGroq

        return ChatGroq(model=_GROQ_MODEL, temperature=0, api_key=key)
    return ChatOpenAI(model=_OPENAI_MODEL, temperature=0)

# ── Agent State ──────────────────────────────────────────────────────────────
class AgentState(TypedDict):
    question:     str
    schema:       str
    sql_query:    str
    results:      str
    column_names: list
    final_answer: str
    error:        str


# ── Node 1: Get Database Schema ───────────────────────────────────────────────
def get_schema(state: AgentState) -> AgentState:
    """Database ki tables aur columns ki information uthata hai"""
    conn   = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()

    schema_parts = []
    for (table_name,) in tables:
        cursor.execute(f"PRAGMA table_info({table_name})")
        cols = cursor.fetchall()

        # Sample data bhi dikhao (2 rows)
        cursor.execute(f"SELECT * FROM {table_name} LIMIT 2")
        sample = cursor.fetchall()

        col_info = ", ".join(f"{c[1]} {c[2]}" for c in cols)
        schema_parts.append(
            f"Table '{table_name}': ({col_info})\n  Sample: {sample}"
        )

    conn.close()
    schema = "\n\n".join(schema_parts)
    return {**state, "schema": schema, "error": ""}


# ── Node 2: Generate SQL ──────────────────────────────────────────────────────
def generate_sql(state: AgentState) -> AgentState:
    """Natural language ko SQLite query mein convert karta hai"""
    llm = _make_llm()

    system_prompt = f"""You are an expert SQL analyst. Convert the user's question into a valid SQLite query.

DATABASE SCHEMA:
{state['schema']}

STRICT RULES:
- Return ONLY the raw SQL query — no markdown, no explanation, no backticks
- Use proper SQLite syntax (no ILIKE, use LIKE instead)
- Always add LIMIT 50 unless user asks for all
- For money/totals, use ROUND(..., 2)
- Use meaningful column aliases (e.g. total_revenue, order_count)
- For date filtering, use strftime or direct string comparison (YYYY-MM-DD)
"""

    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=state["question"]),
    ]

    response = llm.invoke(messages)
    sql = response.content.strip().replace("```sql", "").replace("```", "").strip()
    return {**state, "sql_query": sql}


# ── Node 3: Execute SQL ───────────────────────────────────────────────────────
def execute_sql(state: AgentState) -> AgentState:
    """SQL query run karta hai aur results return karta hai"""
    try:
        conn   = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(state["sql_query"])
        rows    = cursor.fetchall()
        columns = [d[0] for d in cursor.description] if cursor.description else []
        conn.close()

        if rows:
            header = " | ".join(columns)
            lines  = [header, "-" * len(header)]
            for row in rows[:30]:
                lines.append(" | ".join(str(v) for v in row))
            result_str = "\n".join(lines)
        else:
            result_str = "No results found."

        return {**state, "results": result_str, "column_names": columns, "error": ""}

    except Exception as e:
        return {**state, "results": "", "column_names": [], "error": str(e)}


# ── Node 4: Format Answer ─────────────────────────────────────────────────────
def format_answer(state: AgentState) -> AgentState:
    """Results ko business-friendly language mein explain karta hai"""

    # Agar SQL error tha
    if state.get("error"):
        return {
            **state,
            "final_answer": (
                f"❌ **Query Error:** {state['error']}\n\n"
                f"**SQL Tried:** `{state['sql_query']}`\n\n"
                "Please rephrase your question."
            ),
        }

    llm = _make_llm()

    messages = [
        SystemMessage(content=(
            "You are a friendly business data analyst. "
            "Explain the SQL results clearly and concisely in 2-4 sentences. "
            "Highlight the most important insight. "
            "Use dollar signs for money values. "
            "Do NOT repeat the raw data table — just summarize."
        )),
        HumanMessage(content=(
            f"Question: {state['question']}\n\n"
            f"SQL Query Used:\n{state['sql_query']}\n\n"
            f"Raw Results:\n{state['results']}"
        )),
    ]

    response = llm.invoke(messages)
    return {**state, "final_answer": response.content}


# ── Build the Graph ───────────────────────────────────────────────────────────
def create_sql_agent():
    """LangGraph workflow compile karta hai"""
    workflow = StateGraph(AgentState)

    workflow.add_node("get_schema",    get_schema)
    workflow.add_node("generate_sql",  generate_sql)
    workflow.add_node("execute_sql",   execute_sql)
    workflow.add_node("format_answer", format_answer)

    workflow.set_entry_point("get_schema")
    workflow.add_edge("get_schema",    "generate_sql")
    workflow.add_edge("generate_sql",  "execute_sql")
    workflow.add_edge("execute_sql",   "format_answer")
    workflow.add_edge("format_answer", END)

    return workflow.compile()


# ── Quick CLI Test ────────────────────────────────────────────────────────────
if __name__ == "__main__":
    agent = create_sql_agent()

    test_questions = [
        "Who are the top 3 customers by total spending?",
        "What is total revenue by product category?",
        "How many orders are still pending?",
        "Which product has the highest sales?",
    ]

    for q in test_questions:
        print(f"\n{'='*60}")
        print(f"❓ Question: {q}")
        result = agent.invoke({
            "question": q, "schema": "", "sql_query": "",
            "results": "", "column_names": [], "final_answer": "", "error": ""
        })
        print(f"📝 SQL: {result['sql_query']}")
        print(f"📊 Data:\n{result['results']}")
        print(f"💬 Answer: {result['final_answer']}")
