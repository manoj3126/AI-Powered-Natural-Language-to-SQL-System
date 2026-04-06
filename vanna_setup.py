# vanna_setup

import os
from dotenv import load_dotenv

# Core Vanna imports
from vanna import Agent, AgentConfig
from vanna.core.registry import ToolRegistry
from vanna.core.user import UserResolver, User, RequestContext

# Tools
from vanna.tools import RunSqlTool, VisualizeDataTool
from vanna.tools.agent_memory import (
    SaveQuestionToolArgsTool,
    SearchSavedCorrectToolUsesTool,
    SaveTextMemoryTool
)

# Integrations
from vanna.integrations.sqlite import SqliteRunner
from vanna.integrations.local.agent_memory import DemoAgentMemory
from vanna.integrations.google import GeminiLlmService

# Load environment variables
load_dotenv()

# create an LLM service (Gemini)
llm = GeminiLlmService(
    model="gemini-2.5-flash",  
    api_key=os.getenv("GOOGLE_API_KEY")
)

# Database Setup
sql_runner = SqliteRunner(
    database_path="clinic.db"   # use relative path (important for submission)
)
run_sql_tool = RunSqlTool(sql_runner=sql_runner)

# Memory
agent_memory = DemoAgentMemory(max_items=1000)

# Tool Registry
tool_registry = ToolRegistry()

tool_registry.register_local_tool(run_sql_tool, access_groups=['admin', 'user'])
tool_registry.register_local_tool(SaveQuestionToolArgsTool(), access_groups=['admin'])
tool_registry.register_local_tool(SearchSavedCorrectToolUsesTool(), access_groups=['admin', 'user'])
tool_registry.register_local_tool(SaveTextMemoryTool(), access_groups=['admin', 'user'])


# Visualization
from vanna.tools import VisualizeDataTool

tool_registry.register_local_tool(
    VisualizeDataTool(),
    access_groups=['users']   # Who can use this tool
)


# User Resolver
class SimpleUserResolver(UserResolver):
    async def resolve_user(self, request_context: RequestContext) -> User:
        user_email = request_context.get_cookie("vanna_email") or "guest@example.com"
        group = "admin" if user_email == "admin@example.com" else "user"
        return User(id=user_email, email=user_email, group_memberships=[group])


user_resolver = SimpleUserResolver()

# Agent 

agent = Agent(
    llm_service=llm,              # The AI brain
    tool_registry=tool_registry,  # Available capabilities
    user_resolver=user_resolver,  # How to identify users
    agent_memory=agent_memory,    # Tool usage learning
    config=AgentConfig()          # Settings
)


# FastAPI Server (Built-in)
# from vanna.servers.fastapi import VannaFastAPIServer

# server = VannaFastAPIServer(agent)