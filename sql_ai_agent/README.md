# 🤖 SQL AI Agent
### "Ask your database anything in plain English"

Built with **Python + LangGraph + OpenAI + Streamlit**

---

## ✨ What This Does

This AI Agent lets anyone talk to a business database using plain English.
No SQL knowledge required. The agent:

1. **Understands** your question (English)
2. **Generates** the correct SQL query automatically
3. **Executes** it on your database
4. **Explains** the results in simple language

---

## 🚀 Quick Start (3 Steps)

### Step 1 — Install dependencies
```bash
pip install -r requirements.txt
```

### Step 2 — Setup database
```bash
python setup_db.py
```

### Step 3 — Run the app
```bash
streamlit run app.py
```

Then open: **http://localhost:8501**

---

## 🔑 API Key

Get a free/paid OpenAI API key from: https://platform.openai.com/api-keys

Enter it in the sidebar when the app opens.

---

## 💬 Example Questions You Can Ask

| Question | What It Does |
|----------|-------------|
| "Who are top 5 customers by spending?" | Revenue analysis |
| "What is total revenue by category?" | Sales breakdown |
| "How many orders are pending?" | Status report |
| "Which product sold the most?" | Best seller |
| "Show orders from Pakistan customers" | Filtered data |
| "What is average order value per country?" | Geographic analysis |

---

## 🏗️ Project Structure

```
sql_ai_agent/
├── app.py          # Streamlit UI
├── sql_agent.py    # LangGraph Agent (core AI logic)
├── setup_db.py     # Database setup with sample data
├── business.db     # SQLite database (auto-created)
├── requirements.txt
└── README.md
```

---

## ⚙️ How It Works (LangGraph Flow)

```
User Question
     ↓
[Node 1] Get Schema   → reads database structure
     ↓
[Node 2] Generate SQL → GPT-4o-mini writes the query
     ↓
[Node 3] Execute SQL  → runs query on SQLite
     ↓
[Node 4] Format Answer → AI explains results in English
     ↓
Final Answer + Data Table
```

---

## 🎯 Use Cases (For Clients)

- **E-commerce stores** → Sales analytics without hiring data analyst
- **Small businesses** → Inventory & revenue tracking
- **Restaurants** → Order patterns & popular items
- **Any business with data** → Instant insights

---

## 💰 Pricing Suggestions (Upwork/Freelance)

| Service | Price Range |
|---------|------------|
| Basic SQL Agent (this project) | $300 - $500 |
| Custom database integration | $500 - $800 |
| Full dashboard + agent combo | $800 - $1,500 |
| Ongoing maintenance (monthly) | $100 - $200/mo |

---

## 🔧 Customization

To connect your own database, edit `sql_agent.py`:
```python
DB_PATH = "your_database.db"  # Change this
```

To use PostgreSQL/MySQL instead of SQLite:
```python
# Replace sqlite3 with psycopg2 or mysql-connector
import psycopg2
conn = psycopg2.connect("your_connection_string")
```

---

## 📞 Contact

Built by: **Muhammad Arfan Wazeer (AI Automation Engineer)**  
Available for custom projects on Upwork & LinkedIn

---

*Built with ❤️ using LangGraph, OpenAI, and Streamlit*
