
import os
from agents import Agent, RunContextWrapper, Runner, AsyncOpenAI, RunConfig, OpenAIChatCompletionsModel, set_tracing_disabled, RunHooks, AgentHooks, enable_verbose_stdout_logging # type:ignore
from dotenv import load_dotenv, find_dotenv # type: ignore
from agents.extensions.models.litellm_model import LitellmModel # type: ignore
from typing import TypeVar
from dataclasses import dataclass, field
enable_verbose_stdout_logging()
set_tracing_disabled(True)
#? step 1: load the environment variables 
gemini_api_key = os.getenv("GEMINI_API_KEY")

load_dotenv(find_dotenv())

#! open router configurations 
open_router_api_key = os.getenv("OPENROUTER_API_KEY")
#? step 2: setting up the external client  
provider = AsyncOpenAI(
    api_key=gemini_api_key,
    base_url='https://generativelanguage.googleapis.com/v1beta/openai/'
)

#? step 3: setting up the Chat Completions Model
model = OpenAIChatCompletionsModel(
    model = 'gemini-2.0-flash', 
    openai_client = provider,
)

@dataclass
class MyInput:
    name: str
    age: int

# Instantiate user input
user1 = MyInput(name="Mohsin", age=19)

# Define custom hooks for the Runner
class MyCustomRunnerClass(RunHooks):
    def on_agent_start(self, context: RunContextWrapper[MyInput], agent: Agent) -> None:
        print(f'{context.context.name} is starting and {context.context.name} is querying a question')

# Define custom hooks for the Agent
class MyCustomAgent(AgentHooks):
    def on_start(self, context: RunContextWrapper[MyInput], agent: Agent) -> None:
        print(f'{agent.name} is starting and {context.context.name} is querying a question')
    
# #? step 4: setting up the configuration for the agent 

run_config = RunConfig(
    model = model,
    model_provider = provider,
    tracing_disabled = True,
)

Spanish_agent:Agent = Agent(
    name='Assistant',
    instructions='You are an agent - please keep going until the user’s query is completely resolved, before ending your turn and yielding back to the user. Only terminate your turn when you are sure that the problem is solved. You,r Task is to Translate English into Spanish only translate when user ask to translate in other language otherwise return output in english and also call the user name in every messege by using the context',
    model = LitellmModel(model='deepseek/deepseek-r1-0528-qwen3-8b:free', api_key=open_router_api_key),
    hooks=MyCustomAgent
)
try:
    Result = Runner.run_sync(Spanish_agent, 'what is my name', hooks=MyCustomRunnerClass(),run_config=run_config)
    print(Result.final_output)
except SyntaxError as se:
    print(se)
except KeyError as ke:
    print(ke)
except RuntimeError as re:
    print(re)
# import os
# from agents import Agent, RunContextWrapper, Runner, AsyncOpenAI, RunConfig, enable_verbose_stdout_logging, set_tracing_disabled, RunHooks, AgentHooks
# from dotenv import load_dotenv, find_dotenv
# from agents.extensions.models.litellm_model import LitellmModel
# from dataclasses import dataclass

# # Enable logging and disable tracing
# enable_verbose_stdout_logging()
# set_tracing_disabled(True)

# # Load environment variables
# load_dotenv(find_dotenv())
# open_router_api_key = os.getenv("OPENROUTER_API_KEY")

# # Define input dataclass
# @dataclass
# class MyInput:
#     name: str
#     age: int

# # Instantiate user input
# user1 = MyInput(name="Mohsin", age=19)

# # Define custom hooks for the Runner
# class MyCustomRunnerClass(RunHooks):
#     def on_agent_start(self, context: RunContextWrapper[MyInput], agent: Agent) -> None:
#         print(f'{context.context.name} is starting and {context.context.name} is querying a question')

# # Define custom hooks for the Agent
# class MyCustomAgent(AgentHooks):
#     def on_start(self, context: RunContextWrapper[MyInput], agent: Agent) -> None:
#         print(f'{agent.name} is starting and {context.context.name} is querying a question')

# # Set up run configuration
# run_config = RunConfig(
#     tracing_disabled=True
# )

# # Define the agent
# Spanish_agent = Agent(
#     name='Assistant',
#     instructions='You are an agent - please keep going until the user’s query is completely resolved, before ending your turn and yielding back to the user. Only terminate your turn when you are sure that the problem is solved. Your task is to translate English into Spanish only when the user asks to translate; otherwise, return output in English and address the user by name using the context.',
#     model=LitellmModel(model='deepseek/deepseek-r1-0528-qwen3-8b:free', api_key=open_router_api_key),
#     hooks=MyCustomAgent()  # Pass an instance of MyCustomAgent
# )

# # Run the agent
# try:
#     Result = Runner.run_sync(
#         Spanish_agent,
#         'What is my name?',
#         hooks=MyCustomRunnerClass(),
#         run_config=run_config,
#         context=user1  # Pass the context
#     )
#     print(Result.final_output)
# except Exception as e:
#     print(f"Error: {e}")