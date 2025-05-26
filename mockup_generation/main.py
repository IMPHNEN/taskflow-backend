import notte
from prompt import prompt_task
from agno.agent import Agent, RunResponse
from agno.models.openai import OpenAIChat


def create_query(info, brd):
    agent = Agent(
    model=OpenAIChat(id="gpt-4o-mini"),
    role="You are a highly skilled Prompt Engineer tasked with crafting a precise and actionable prompt for the Lovable AI tool, which generates website mockups.",
    expected_output="A clear, well-structured prompt, ready to be processed directly by the Lovable AI tool, with no extraneous explanation or conversation.",
    reasoning=True,
    context={
        "Project Context": info,
        "Business Requirements Document": brd
    },
    add_context=True)

    response: RunResponse = agent.run("From the Project Context and Business Requirements Document, generate a Prompt for a AI Tools called Lovable that will generate mockups for a website.")
    return response.content

def main(info, brd, lovable_email, lovable_password):
    query = create_query(info=info, brd=brd)

    agi = notte.Agent(reasoning_model="openrouter/google/gemma-3-27b-it", max_steps=20, use_vision=True)

    task = prompt_task.format(email=lovable_email, password=lovable_password, query=query)

    agi.run(task=task, url="https://lovable.dev/login")

if __name__ == "__main__":
    main(info="", brd="", lovable_email="", lovable_password="")
