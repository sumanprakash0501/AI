from agents import Runner, trace, gen_trace_id
from search_agent import search_agent
from planner_agent import web_search_planner_agent, WebSearchPlan, WebSearchItem
from report_writer_agent import report_writer_agent, ReportData
from email_agent import email_agent
import asyncio

class SearchManager:

    async def run(self, query:str):
        """Run the deep research process, Yielding the status update and Final report"""
        trace_id = gen_trace_id()
        with trace("Research Trace", trace_id=trace_id):
            print(f"View trace: https://platform.openai.com/traces/trace?trace_id={trace_id}")
            yield f"View trace: https://platform.openai.com/traces/trace?trace_id={trace_id}"
            print("Starting research...")
            search_plan = await self.plan_searches(query)
            yield "Searches planned, starting to search..."     
            search_results = await self.perform_searches(search_plan)
            yield "Searches complete, writing report..."
            report = await self.write_report(query, search_results)
            yield "Report written, sending email..."
            await self.send_email(report)
            yield "Email sent, research complete"
            yield report.markdown_report
        
    async def plan_searches(self, query:str):
        """Use the web_search_planner_agent to plan the search terms that need to be searched on web"""
        print("Planning Search Terms...")
        result = await Runner.run(web_search_planner_agent, f"Query:{query}")
        print(f"Will perform {len(result.final_output.search_terms)} searches")
        return result.final_output


    async def search(self, search_item:WebSearchItem):
        """Use the search_agent to do a websearch for the given search_item"""
        input = f"Search term:{search_item.search_term}\nReason for search:{search_item.reason}"
        result= await Runner.run(search_agent,input)
        return result.final_output

    async def perform_searches(self, search_plan:WebSearchPlan):
        """Execute search() for each item in search_terms"""
        print("Searching...")
        tasks = [asyncio.create_task(self.search(search_term)) for search_term in search_plan.search_terms]
        result = asyncio.gather(*tasks)
        print("Finished Searching...")
        return result

    async def write_report(self, query:str, search_results:list[str]):
        """Use the report_writer_agent to write a report based on the search results."""
        print("Thinking about report....")
        input=f"Query:{query}\nSummarized Search Result:{search_results}"
        result= await Runner.run(report_writer_agent, input)
        print("Report Generated...")
        return result.final_output

    async def send_email(self, report:ReportData):
        """use email_agent to send the given report"""
        print("Writing Email...")
        result = await Runner.run(email_agent,report.markdown_report)
        print("Email sent.")
        return report