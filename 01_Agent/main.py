import os
from agents import Agent, Runner, AsyncOpenAI, RunConfig, OpenAIChatCompletionsModel # type:ignore
from dotenv import load_dotenv, find_dotenv # type: ignore

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


#? step 5: setting up the agent

agent:Agent = Agent(
    name='Assistant',
    instructions='A helpful assistant',
    model = model,
)
Result = Runner.run_sync(agent, 'what is the capital of France?', run_config=run_config)
print(Result.final_output)

