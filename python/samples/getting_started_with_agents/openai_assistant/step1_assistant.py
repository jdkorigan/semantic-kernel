# Copyright (c) Microsoft. All rights reserved.
import asyncio
import os
script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)

from dotenv import load_dotenv

from semantic_kernel.agents import AssistantAgentThread, AzureAssistantAgent

"""
The following sample demonstrates how to create an OpenAI assistant using either
Azure OpenAI or OpenAI. The sample shows how to have the assistant answer
questions about the world.

The interaction with the agent is via the `get_response` method, which sends a
user input to the agent and receives a response from the agent. The conversation
history is maintained by the agent service, i.e. the responses are automatically
associated with the thread. Therefore, client code does not need to maintain the
conversation history.
"""

# Simulate a conversation with the agent
USER_INPUTS = [
    "Why is the sky blue?",
    "What is the speed of light?",
    "What have we been talking about?",
]


async def main():
    load_dotenv()

    deployment_name = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
    
    # 1. Create the client using Azure OpenAI resources and configuration
    client = AzureAssistantAgent.create_client(deployment_name=deployment_name)

    # 2. Create the assistant on the Azure OpenAI service
    definition = await client.beta.assistants.create(
        model=deployment_name,
        instructions="Answer questions about the world in one sentence.",
        name="Assistant",
    )

    # 3. Create a Semantic Kernel agent for the Azure OpenAI assistant
    agent = AzureAssistantAgent(
        client=client,
        definition=definition,
    )

    # 4. Create a new thread for use with the assistant
    # If no thread is provided, a new thread will be
    # created and returned with the initial response
    thread: AssistantAgentThread = None

    try:
        for user_input in USER_INPUTS:
            print(f"# User: '{user_input}'")
            # 6. Invoke the agent for the current thread and print the response
            response = await agent.get_response(messages=user_input, thread=thread)
            print(f"# {response.message.role}: {response.message.content}")
            thread = response.thread
    finally:
        # 7. Clean up the resources
        if thread:
            await thread.delete()
        if agent.id:
            await agent.client.beta.assistants.delete(assistant_id=agent.id)

    """
    You should see output similar to the following:

    # User: 'Why is the sky blue?'
    # assistant: The sky appears blue because molecules in the atmosphere scatter sunlight in all directions, and blue
        light is scattered more than other colors because it travels in shorter, smaller waves.
    # User: 'What is the speed of light?'
    # assistant: The speed of light in a vacuum is approximately 299,792,458 meters per second
        (about 186,282 miles per second).
     """


if __name__ == "__main__":
    asyncio.run(main())
