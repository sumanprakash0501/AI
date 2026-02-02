# Imports
from dotenv import load_dotenv
from openai import OpenAI
from pypdf import PdfReader
from IPython.display import Markdown, display
import os
import json
import requests
import gradio as gr

# load dotenv file and initialize openai client
load_dotenv(override=True)


# Def push method to send push messages to the user
def push(message):
    pushover_user = os.getenv("PUSHOVER_USER")
    pushover_token = os.getenv("PUSHOVER_TOKEN")
    pushover_url = "https://api.pushover.net/1/messages.json"
    #print(f"Push:{message}")
    payload = {"user":pushover_user, "token":pushover_token, "message":message}
    requests.post(pushover_url,data=payload)

# Create a record_user_details function that will record the user details who looks interested in your profile
def record_user_details(email, name="Name not provided", notes="not provided"):
    push(f"Recording interest from {name} with email: {email} and notes: {notes}")
    return {"Recorded":"OK"}

# Create a record_unknown_question function that will record the Questions that AI agent can't answer
def record_unknown_question(question):
    push(f"Recording {question} that I couldn't answer.")
    return {"Recorded":"Ok"}

# Create a json file for record_user_details function to give a context to LLM about the function which is going to be used as a tool by LLM
record_user_details_json={
    "name":"record_user_details",
    "description": "Use this tool to records the details of user if they are interested in being in touch and provided their email id",
    "parameters":{
        "type":"object",
        "properties":{
            "email":{
                "type": "string",
                "description": "The email id of this user"
                    },
            "name":{
                "type": "string",
                "description": "The name of this user if they provided it"
                    },
            "notes":{
                "type": "string",
                "description": "Any additional information about the conversation that's worth recording to give context"
                    }},
        "required": ["email"],
        "additionalProperties": False
        }
}

# Create a json file for record_unknown_question function to share a context with LLM about this function that is going to provided as a Tool
record_unknown_question_json ={
    "name": "record_unknown_question",
    "description": "Always use this tool to record any question that you can't answer as you don't know the answer, even if it's about something trivial or unrelated to career.",
    "parameters":{
        "type":"object",
        "properties":{
            "question":{
                "type": "string",
                "description": "The question asked that can't be answered."}
        },
        "required": ["question"],
        "additionalProperties": False
    }
}

# Create a list of tools for the LLM
tools = [{"type":"function", "function":record_user_details_json},
        {"type":"function", "function":record_unknown_question_json}]

class Me:
    def __init__(self) -> None:
         self.openai = OpenAI()
         self.name = "Suman Prakash"

         # Build paths relative to this file so it works no matter the working directory
         base_dir = os.path.dirname(os.path.abspath(__file__))
         me_dir = os.path.join(base_dir, "me")
         pdf_path = os.path.join(me_dir, "SumanPrakash_LinkedIn.pdf")
         summary_path = os.path.join(me_dir, "summary.txt")

         reader = PdfReader(pdf_path)
         self.linkedin = ""
         for page in reader.pages:
            text = page.extract_text()
            if text:
                self.linkedin += text
         with open(summary_path, "r", encoding="utf-8") as f:
            self.summary = f.read()

    def handle_tool_call(self, tool_calls):
        results = []
        for tool_call in tool_calls:
            tool_name = tool_call.function.name
            arguments = json.loads(tool_call.function.arguments)
            print(f"Tool called: {tool_name}", flush=True)
            tool = globals().get(tool_name)
            result = tool(**arguments) if tool else {}
            results.append({"role": "tool","content": json.dumps(result),"tool_call_id": tool_call.id})
        return results

    def system_prompt(self):
        # Generate a system prompt 
        system_prompt = f"""You are acting as {self.name}. You are answering questions on {self.name}'s website, 
particularly questions related to {self.name}'s career, background, skills and experience. 
Your responsibility is to represent {self.name} for interactions on the website as faithfully as possible. 
You are given a summary of {self.name}'s background and LinkedIn profile which you can use to answer questions. 
Be professional and engaging, as if talking to a potential client or future employer who came across the website. 
If you don't know the answer, say so.

With this context, please chat with the user, always staying in character as {self.name}.

PFB the summary and Linkedin Profile as resource that you need to refer for answering questions or 
communicating with the user on other side.

## Summary:\n{self.summary}\n\n
## LinkedIn Profile:\n{self.linkedin}

NOTE: You can use following tools provided to you:
1. If the user is engaging in discussion, try to steer them towards getting in touch via email; ask for their email and record it using your record_user_details tool.
2. If you don't know the answer to any question, use your record_unknown_question tool to record the question that you couldn't answer, even if it's about something trivial or unrelated to career.
"""
        return system_prompt

    def chat(self, message, history):
        messages = [{"role": "system", "content": self.system_prompt()}] + history + [{"role": "user", "content": message}]
        done = False
        while not done:
            response = self.openai.chat.completions.create(model="gpt-4o-mini", messages=messages, tools=tools)
            if response.choices[0].finish_reason=="tool_calls":
                message = response.choices[0].message
                tool_calls = message.tool_calls
                results = self.handle_tool_call(tool_calls)
                messages.append(message)
                messages.extend(results)
            else:
                done = True
        return response.choices[0].message.content

if __name__ == "__main__":
    me = Me()
    gr.ChatInterface(me.chat).launch(share=True)