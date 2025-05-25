import notte
import os
from prompt import prompt_task

agi = notte.Agent(reasoning_model="openrouter/google/gemma-3-27b-it", max_steps=20, use_vision=True)

os.environ["OPENROUTER_API_KEY"] = "sk-"
# os.environ["CEREBRAS_API_KEY"] = "csk-"
# os.environ["GROQ_API_KEY"] = "gsk_"


query = """
> “Create a clean, responsive homepage mockup for a modern AI consulting agency.
>
> The website should include:
>
> * Hero section with a headline, subheadline, and call-to-action button
> * About us section with 3 bullet points
> * Services section highlighting: LLM Integration, Custom AI Agents, and Automation Tools
> * Testimonials from clients
> * Contact form at the bottom
>
> Design style: Minimalist, professional, and futuristic. Use a light theme with blue and black as accent colors.”
"""

task = prompt_task.format(email="@gmail.com", password="@akupassword", query=query)

agi.run(task=task, url="https://lovable.dev/login")