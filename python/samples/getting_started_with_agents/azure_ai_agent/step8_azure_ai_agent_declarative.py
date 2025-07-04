# Copyright (c) Microsoft. All rights reserved.
import os
script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)

import asyncio
from typing import Annotated

from azure.identity.aio import DefaultAzureCredential

from semantic_kernel.agents import AgentRegistry, AzureAIAgent, AzureAIAgentSettings
from semantic_kernel.functions import kernel_function
from semantic_kernel.kernel import Kernel

"""
The following sample demonstrates how to create an Azure AI agent that answers
questions about a sample menu using a Semantic Kernel Plugin. The agent is created
using a yaml declarative spec.
"""


# Define a sample plugin for the sample
class MenuPlugin:
    """A sample Menu Plugin used for the concept sample."""

    @kernel_function(description="Provides a list of specials from the menu.")
    def get_specials(self) -> Annotated[str, "Returns the specials from the menu."]:
        return """
        Special Soup: Clam Chowder
        Special Salad: Cobb Salad
        Special Drink: Chai Tea
        """

    @kernel_function(description="Provides the price of the requested menu item.")
    def get_item_price(
        self, menu_item: Annotated[str, "The name of the menu item."]
    ) -> Annotated[str, "Returns the price of the menu item."]:
        return "$9.99"


# Simulate a conversation with the agent
USER_INPUTS = [
    "Hello",
    "What is the special soup?",
    "How much does that cost?",
    "Thank you",
]

# Define the YAML string for the sample
SPEC = """
type: foundry_agent
name: Host
instructions: Respond politely to the user's questions.
model:
  id: ${AzureAI:ChatModelId}
tools:
  - id: MenuPlugin.get_specials
    type: function
  - id: MenuPlugin.get_item_price
    type: function
"""


async def main() -> None:
    ai_agent_settings = AzureAIAgentSettings()
    async with (
        DefaultAzureCredential() as creds,
        AzureAIAgent.create_client(credential=creds) as client,
    ):
        # 1. Create a Kernel instance
        # For declarative agents, the kernel is required to resolve the plugin(s)
        kernel = Kernel()
        kernel.add_plugin(MenuPlugin())

        # 2. Create a Semantic Kernel agent for the Azure AI agent
        agent: AzureAIAgent = await AgentRegistry.create_from_yaml(
            SPEC,
            kernel=kernel,
            settings=ai_agent_settings,
            client=client,
        )

        # 3. Create a thread for the agent
        # If no thread is provided, a new thread will be
        # created and returned with the initial response
        thread = None

        try:
            for user_input in USER_INPUTS:
                print(f"# User: {user_input}")
                # 4. Invoke the agent for the specified thread for response
                async for response in agent.invoke(
                    messages=user_input,
                    thread=thread,
                ):
                    print(f"# {response.name}: {response}")
                    thread = response.thread
        finally:
            # 5. Cleanup: Delete the thread and agent
            await thread.delete() if thread else None
            await client.agents.delete_agent(agent.id)

        """
        Sample Output:
        # User: Hello
        # Agent: Hello! How can I assist you today?
        # User: What is the special soup?
        # ...
        """


if __name__ == "__main__":
    asyncio.run(main())
