from chromadb import Client # type: ignore
from chromadb.config import Settings # type: ignore
import os

# Initialize Chroma DB client
chroma_client = Client(Settings(chroma_api_impl="rest", chroma_server_host="localhost", chroma_server_http_port="8000"))

# Create a collection (vector store) in Chroma DB
collection = chroma_client.create_collection(name="my_knowledge_base")

# Add documents to the collection (replace with your own data)
documents = [
    {"text": "This is document 1", "metadata": {"source": "doc1"}},
    {"text": "This is document 2", "metadata": {"source": "doc2"}},
    # Add more documents as needed
]

# Add documents to the collection
collection.add(
    documents=[doc["text"] for doc in documents],
    metadatas=[doc["metadata"] for doc in documents],
    ids=[str(i) for i in range(len(documents))]
)



# ======================
from agents import Agent, Runner, AsyncOpenAI, RunConfig, OpenAIChatCompletionsModel, Tool # type:ignore
from dotenv import load_dotenv, find_dotenv # type: ignore
import os
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