from agents import Agent
from pydantic import BaseModel, Field
HOW_MANY_SEARCHES = 3
INSTRUCTIONS = f"""You are a research assistant. Given a query you need to come with {HOW_MANY_SEARCHES} search terms. Be careful in providing the search term as these search terms provided by you will be searched on web to find the answer
for the query. Your goal should be providing the effective search terms that when it gets searched the search results should help answring the query."""

class WebSearchItem(BaseModel):
    reason: str = Field(description="Your reasoning for why this search term is helpful in answering the query")
    search_term: str = Field(description="The search term to use for the web search")

class WebSearchPlan(BaseModel):
    search_terms:list[WebSearchItem] = Field(description="A list of all the search terms for web search to better answer the question")

web_search_planner_agent = Agent(name="Web Search Planner",
instructions=INSTRUCTIONS,
model="gpt-4o-mini",
output_type=WebSearchPlan)
