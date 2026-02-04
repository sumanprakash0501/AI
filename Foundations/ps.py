#imports
from email import message
from rich.console import Console
from dotenv import load_dotenv
from openai import OpenAI
import json
import gradio as gr
#load devenv
load_dotenv(override=True)
#Define show method
def show(text):
    try:
        Console().print(text)
    except Exception:
        print(text)
#initiate Openai client
openai = OpenAI()
todos, completed = [], []

# def get_todo_report function
def get_todo_report()->str:
    result = ""
    for index,todo in enumerate(todos):
        if completed[index]:
            result += f"Todo #{index+1}: [green][strike]{todo}[/strike][/green]\n"
        else:
            result += f"Todo #{index+1}: {todo}\n"
    show(result)
    return result

# def create_todos() function
def create_todos(descriptions: list[str]) -> str:
    todos.extend(descriptions)
    completed.extend([False] * len(descriptions))
    return get_todo_report()

# def markcomplete() fuinction
def mark_complete(index:int, completion_notes:str)-> str:
    if 1 <= index <= len(todos):
        completed[index-1]= True
    else:
        return "No to do at this Index"
    Console().print(completion_notes)
    return get_todo_report()    

create_todos_json = {
    "name": "create_todos",
    "description": "Add new todos from a list of descriptions and return the full list",
    "parameters": {
        "type": "object",
        "properties": {
            "descriptions": {
                'type': 'array',
                'items': {'type': 'string'},
                'title': 'Descriptions'
                }
            },
        "required": ["descriptions"],
        "additionalProperties": False
    }
}

mark_complete_json = {
    "name": "mark_complete",
    "description": "Mark complete the todo at the given position (starting from 1) and return the full list",
    "parameters": {
        'properties': {
            'index': {
                'description': 'The 1-based index of the todo to mark as complete',
                'title': 'Index',
                'type': 'integer'
                },
            'completion_notes': {
                'description': 'Notes about how you completed the todo in rich console markup',
                'title': 'Completion Notes',
                'type': 'string'
                }
            },
        'required': ['index', 'completion_notes'],
        'type': 'object',
        'additionalProperties': False
    }
}

tools= [{"type":"function", "function":create_todos_json},
        {"type":"function","function":mark_complete_json}]

def handle_tool_calls(tool_calls):
    results = []
    for tool_call in tool_calls:
        tool_name = tool_call.function.name
        arguments = json.loads(tool_call.function.arguments)
        tool = globals().get(tool_name)
        result = tool(**arguments) if tool else {}
        results.append({"role":"tool", "content":json.dumps(result),"tool_call_id":tool_call.id})
    return results

def loop(messages):
    done = False
    while not done:
        response = openai.chat.completions.create(model="gpt-4o-mini", messages=messages, tools=tools)
        finish_reason = response.choices[0].finish_reason
        if finish_reason=="tool_calls":
            message = response.choices[0].message
            tool_calls = message.tool_calls
            results = handle_tool_calls(tool_calls)
            messages.append(message)
            messages.extend(results)
        else:
            done = True
    show(response.choices[0].message.content)

system_message = """
You are given a problem to solve, by using your todo tools to plan a list of steps, then carrying out each step in turn.
Now use the todo list tools, create a plan, carry out the steps, and reply with the solution.
If any quantity isn't provided in the question, then include a step to come up with a reasonable estimate.
Provide your solution in Rich console markup without code blocks.
Do not ask the user questions or clarification; respond only with the answer after using your tools.
"""
user_message = """"
A bag contains 2 red, 3 green and 2 blue balls. Two balls are drawn at random. What is the probability that none of the balls drawn is blue
"""
messages = [{"role": "system", "content": system_message}, {"role": "user", "content": user_message}]

loop(messages)

#if __name__ == "__main__":
 #   gr.Interface(loop,"text", "text").launch

