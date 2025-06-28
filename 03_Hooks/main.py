
import os
from agents import Agent, RunContextWrapper, Runner, AsyncOpenAI, RunConfig, OpenAIChatCompletionsModel, set_tracing_disabled, RunHooks, AgentHooks, enable_verbose_stdout_logging, function_tool # type:ignore
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
    location:str

# Instantiate user input
user1 = MyInput(name="Mohsin", age=19, location='karachi')

# Define custom hooks for the Runner
class MyCustomRunnerClass(RunHooks):
    def on_agent_start(context: RunContextWrapper[MyInput]):
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

@function_tool
def location_tool(ctx:RunContextWrapper[MyInput]):
    print(f'{ctx.context.name} is {ctx.context.age} Year old')
    

Spanish_agent:Agent = Agent(
    name='Assistant',
    instructions='You are an agent - please keep going until the user’s query is completely resolved, before ending your turn and yielding back to the user. Only terminate your turn when you are sure that the problem is solved. You,r Task is to Translate English into Spanish only translate when user ask to translate in other language otherwise return output in english and also call the user name in every messege by using the context',
    model = model,
    hooks=MyCustomAgent(),
    tools=[location_tool]
)
try:
    Result = Runner.run_sync(Spanish_agent, 'what is my name and what is user age', hooks=MyCustomRunnerClass(),context=user1,run_config=run_config)
    print(Result.final_output)
except SyntaxError as se:
    print(se)
except KeyError as ke:
    print(ke)
except RuntimeError as re:
    print(re)
