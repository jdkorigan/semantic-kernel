# Copyright (c) Microsoft. All rights reserved.
#from dotenv import load_dotenv
#load_dotenv()

import os
import asyncio
from typing import Optional
import re

script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)

from azure.identity.aio import DefaultAzureCredential
from semantic_kernel.agents import AzureAIAgent, AzureAIAgentSettings, AzureAIAgentThread

"""
The following sample demonstrates how to create an Azure AI agent that answers
user questions. This sample demonstrates the basic steps to create an agent
and simulate a conversation with the agent.

The interaction with the agent is via the `get_response` method, which sends a
user input to the agent and receives a response from the agent. The conversation
history is maintained by the agent service, i.e. the responses are automatically
associated with the thread. Therefore, client code does not need to maintain the
conversation history.

Required Environment Variables:
- AZURE_AI_AGENT_MODEL_DEPLOYMENT_NAME: The model deployment name for the agent
- AZURE_AI_AGENT_PROJECT_CONNECTION_STRING: The Azure AI Project connection string
"""

# Simulate a conversation with the agent
USER_INPUTS = [
    "Hello, I am John Doe.",
    "What is your name?",
    "What is my name?",
]



async def main() -> None:
    """Main function to demonstrate Azure AI Agent usage with step-by-step validation."""
    try:
        ai_agent_settings = AzureAIAgentSettings()

        async with (
            DefaultAzureCredential() as creds,
            AzureAIAgent.create_client(credential=creds) as client,
        ):
            # 5. Create an agent on the Azure AI agent service
            agent_definition = await client.agents.create_agent(
                model=ai_agent_settings.model_deployment_name,
                name="Assistant",
                description="A helpful assistant that answers user questions.",
                instructions="Answer the user's questions in a helpful and friendly manner.",
            )

            # 6. Create a Semantic Kernel agent for the Azure AI agent
            agent = AzureAIAgent(
                client=client,
                definition=agent_definition,
            )

            # 7. Create a thread for the agent
            thread: Optional[AzureAIAgentThread] = None

            for i, user_input in enumerate(USER_INPUTS, 1):
                print(f"\n--- Conversation Turn {i} ---")
                print(f"# User: {user_input}")
                response = await agent.get_response(messages=user_input, thread=thread)
                print(f"# {response.message.role}: {response.message.content}")
                thread = response.thread

            # 8. Cleanup: Delete the thread and agent
            if thread:
                await thread.delete()
            await client.agents.delete_agent(agent.id)

        """
        Sample Output:
        --- Conversation Turn 1 ---
        # User: Hello, I am John Doe.
        # assistant: Hello, John! How can I assist you today?
        
        --- Conversation Turn 2 ---
        # User: What is your name?
        # assistant: I'm here as your assistant, so you can just call me Assistant. How can I help you today?
        
        --- Conversation Turn 3 ---
        # User: What is my name?
        # assistant: Your name is John Doe. How can I assist you today, John?
        """

    except Exception as e:
        print(f"[FATAL ERROR] {e}")

if __name__ == "__main__":
    asyncio.run(main())
