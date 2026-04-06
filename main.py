
# main.py

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from vanna_setup import agent, agent_memory
from vanna.servers.fastapi import VannaFastAPIServer

# Create Vanna Server (built-in endpoints)
server = VannaFastAPIServer(agent)
app = server.create_app()


# Request Schema
class ChatRequest(BaseModel):
    question: str


# SQL Validation

def validate_sql(sql: str):
    sql_upper = sql.upper()

    # Only SELECT allowed
    if not sql_upper.strip().startswith("SELECT"):
        raise ValueError("Only SELECT queries are allowed")

    # Dangerous keywords
    forbidden = [
        "INSERT", "UPDATE", "DELETE", "DROP", "ALTER",
        "EXEC", "GRANT", "REVOKE", "SHUTDOWN"
    ]

    for word in forbidden:
        if word in sql_upper:
            raise ValueError(f"Forbidden keyword detected: {word}")

    # System tables
    if "SQLITE_MASTER" in sql_upper:
        raise ValueError("Access to system tables is not allowed")


# Custom /chat
@app.post("/chat")
def custom_chat(request: ChatRequest):

    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty")

    try:
        # Ask agent 
        response = agent.send_message(request.question)

        # Extract SQL from tool calls
        sql_query = None

        if hasattr(response, "tool_calls") and response.tool_calls:
            for tool in response.tool_calls:
                if tool.get("name") == "RunSqlTool":
                    sql_query = tool.get("args", {}).get("sql")

        # Validate SQL

        if sql_query:
            validate_sql(sql_query)

        # Extract Data
        columns = []
        rows = []

        if hasattr(response, "data") and response.data is not None:
            df = response.data
            columns = list(df.columns)
            rows = df.values.tolist()

        # Final Response
        return {
            "message": getattr(response, "message", "Success"),
            "sql_query": sql_query,
            "columns": columns,
            "rows": rows,
            "row_count": len(rows),
            "chart": None,      
            "chart_type": None
        }

    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Health Endpoint
@app.get("/health")
def health():
    return {
        "status": "ok",
        "database": "connected",
        "agent_memory_items": "loaded"
    }