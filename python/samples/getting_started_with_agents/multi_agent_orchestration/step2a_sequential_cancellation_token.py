# Copyright (c) Microsoft. All rights reserved.

import os
script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)

from dotenv import load_dotenv

import asyncio
import logging

from semantic_kernel.agents import Agent, ChatCompletionAgent, SequentialOrchestration
from semantic_kernel.agents.runtime import InProcessRuntime
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion

"""
The following sample demonstrates how to cancel an invocation of an orchestration
that is still running.

This sample demonstrates the basic steps of creating and starting a runtime, creating
a sequential orchestration, invoking the orchestration, and cancelling it before it
finishes.
"""

# Set up logging to see the invocation process
logging.basicConfig(level=logging.WARNING)  # Set default level to WARNING
logging.getLogger("semantic_kernel.agents.orchestration.sequential").setLevel(logging.DEBUG)


def get_agents(deployment_name: str) -> list[Agent]:
    """Return a list of agents that will participate in the sequential orchestration.

    Feel free to add or remove agents.
    """
    concept_extractor_agent = ChatCompletionAgent(
        name="ConceptExtractorAgent",
        instructions=(
            "You are a marketing analyst. Given a product description, identify:\n"
            "- Key features\n"
            "- Target audience\n"
            "- Unique selling points\n\n"
        ),
        service=AzureChatCompletion(deployment_name=deployment_name),
    )
    writer_agent = ChatCompletionAgent(
        name="WriterAgent",
        instructions=(
            "You are a marketing copywriter. Given a block of text describing features, audience, and USPs, "
            "compose a compelling marketing copy (like a newsletter section) that highlights these points. "
            "Output should be short (around 150 words), output just the copy as a single text block."
        ),
        service=AzureChatCompletion(deployment_name=deployment_name),
    )
    format_proof_agent = ChatCompletionAgent(
        name="FormatProofAgent",
        instructions=(
            "You are an editor. Given the draft copy, correct grammar, improve clarity, ensure consistent tone, "
            "give format and make it polished. Output the final improved copy as a single text block."
        ),
        service=AzureChatCompletion(deployment_name=deployment_name),
    )

    # The order of the agents in the list will be the order in which they are executed
    return [concept_extractor_agent, writer_agent, format_proof_agent]


async def main():
    load_dotenv()

    deployment_name = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")

    """Main function to run the agents."""
    # 1. Create a sequential orchestration with multiple agents
    agents = get_agents(deployment_name)
    sequential_orchestration = SequentialOrchestration(members=agents)

    # 2. Create a runtime and start it
    runtime = InProcessRuntime()
    runtime.start()

    # 3. Invoke the orchestration with a task and the runtime
    orchestration_result = await sequential_orchestration.invoke(
        task="An eco-friendly stainless steel water bottle that keeps drinks cold for 24 hours",
        runtime=runtime,
    )

    # 4. Cancel the orchestration before it finishes
    await asyncio.sleep(1)  # Simulate some delay before cancellation
    orchestration_result.cancel()

    try:
        # Attempt to get the result will result in an exception due to cancellation
        _ = await orchestration_result.get(timeout=20)
    except Exception as e:
        print(e)
    finally:
        # 5. Stop the runtime
        await runtime.stop_when_idle()

    """
    Sample output:
    DEBUG:semantic_kernel.agents.orchestration.sequential:Registered agent actor of type 
        FormatProofAgent_5efa69d39306414c91325ef82145ec19
    DEBUG:semantic_kernel.agents.orchestration.sequential:Registered agent actor of type
        WriterAgent_5efa69d39306414c91325ef82145ec19
    DEBUG:semantic_kernel.agents.orchestration.sequential:Registered agent actor of type
        ConceptExtractorAgent_5efa69d39306414c91325ef82145ec19
    DEBUG:semantic_kernel.agents.orchestration.sequential:Sequential actor 
        (Actor ID: ConceptExtractorAgent_5efa69d39306414c91325ef82145ec19/default; Agent name: ConceptExtractorAgent)
        started processing...
    The invocation was canceled before it could complete.
    DEBUG:semantic_kernel.agents.orchestration.sequential:Sequential actor
        (Actor ID: ConceptExtractorAgent_5efa69d39306414c91325ef82145ec19/default; Agent name: ConceptExtractorAgent)
        finished processing.
    """


if __name__ == "__main__":
    asyncio.run(main())
