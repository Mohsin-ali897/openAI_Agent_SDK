import os
from agents import Agent, Runner, AsyncOpenAI, RunConfig, OpenAIChatCompletionsModel, RunContextWrapper , function_tool# type:ignore
from dotenv import load_dotenv, find_dotenv # type: ignore
from dataclasses import dataclass
#? step 1: load the environment variables 

load_dotenv(find_dotenv())
gemini_api_key = os.getenv("GEMINI_API_KEY")
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

#? step 4: setting up the configuration for the agent 

run_config = RunConfig(
    model = model,
    model_provider = provider,
    tracing_disabled = True,
)

@dataclass
class UserInfo1:
    name: str
    uid: int
    location: str = "Pakistan"

@function_tool
async def fetch_user_age(wrapper: RunContextWrapper[UserInfo1]) -> str:
    '''Returns the age of the user.'''
    return f"User {wrapper.context.name} is 30 years old"

@function_tool
async def fetch_user_location(wrapper: RunContextWrapper[UserInfo1]) -> str:
    '''Returns the location of the user.'''
    return f"User {wrapper.context.name} is from {wrapper.context.location}"

agent:Agent = Agent(
    name='Assistant',
    instructions='A helpful assistant',
    model = model,
    tools=[fetch_user_age,fetch_user_location]
)
user_info = UserInfo1(name="Muhammad Qasim", uid=123, location='United Kingdom')
Result = Runner.run_sync(agent, 'what is the age of user', run_config=run_config, context=user_info)
print(Result.final_output)
