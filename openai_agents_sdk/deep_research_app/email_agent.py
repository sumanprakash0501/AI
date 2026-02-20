from agents import Agent, function_tool
import sendgrid
import os
from sendgrid.helpers.mail import Mail
@function_tool
def send_html_email(subject:str, html_body:str)->dict[str,str]:
    """ Send out an email with provided subject and HTML Body"""
    sg = sendgrid.SendGridAPIClient(os.getenv("SENDGRID_API_KEY"))
    message = Mail(from_email="sumanprakash.nitp@gmail.com",
    to_emails="bittu1suman2@gmail.com",
    subject=subject,
    html_content=html_body)
    sg.send(message)
    return {"Status":"Success"}

INSTRUCTIONS = """You are able to send a nicely formatted HTML email based on a detailed report.
You will be provided with a detailed report. You should use your tool to send one email, providing the report converted into clean, well presented HTML with an appropriate subject line."""

email_agent = Agent(name="Email Agent",
instructions=INSTRUCTIONS,
model="gpt-4o-mini",
tools=[send_html_email])