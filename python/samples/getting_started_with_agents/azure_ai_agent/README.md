# Azure AI Agent Sample

This sample demonstrates how to create and use an Azure AI Agent with Semantic Kernel 1.34. The Azure AI Agent is a powerful tool that can answer user questions and maintain conversation context through threads.

## Prerequisites

1. **Azure AI Services**: You need access to Azure AI Services with the Azure AI Agent feature enabled.
2. **Python 3.8+**: Ensure you have Python 3.8 or later installed.
3. **Azure Identity**: You need proper Azure authentication setup.

## Environment Variables

Create a `.env` file in the same directory as the sample with the following variables:

```env
# Required: Azure AI Agent Model Deployment Name
AZURE_AI_AGENT_MODEL_DEPLOYMENT_NAME=your-model-deployment-name

# Required: Azure AI Project Connection String
AZURE_AI_AGENT_PROJECT_CONNECTION_STRING=your-project-connection-string

# Optional: Additional Azure AI Agent settings
AZURE_AI_AGENT_ENDPOINT=your-endpoint
AZURE_AI_AGENT_SUBSCRIPTION_ID=your-subscription-id
AZURE_AI_AGENT_RESOURCE_GROUP_NAME=your-resource-group
AZURE_AI_AGENT_PROJECT_NAME=your-project-name
```

## Installation

1. Install the required dependencies:

```bash
pip install semantic-kernel azure-identity python-dotenv
```

2. Ensure you have the Azure CLI installed and are authenticated:

```bash
az login
```

## Running the Sample

Execute the sample script:

```bash
python step1_azure_ai_agent.py
```

## What the Sample Does

1. **Creates an Azure AI Agent**: Uses the Azure AI Project client to create a new agent on the Azure AI service.
2. **Creates a Semantic Kernel Agent**: Wraps the Azure AI agent with Semantic Kernel functionality.
3. **Simulates a Conversation**: Sends multiple user messages to the agent and displays responses.
4. **Maintains Thread Context**: Uses threads to maintain conversation history.
5. **Cleans Up Resources**: Deletes the created agent and thread when done.

## Key Features Demonstrated

- **Agent Creation**: How to create an Azure AI agent with custom instructions
- **Thread Management**: How to use threads for conversation context
- **Error Handling**: Proper error handling for agent operations
- **Resource Cleanup**: Ensuring resources are properly cleaned up
- **Logging**: Comprehensive logging for debugging and monitoring

## Expected Output

```
INFO:__main__:Creating Azure AI Agent client...
INFO:__main__:Creating agent on Azure AI service...
INFO:__main__:Created agent with ID: agent_123456
INFO:__main__:Created Semantic Kernel agent: Assistant

--- Conversation Turn 1 ---
# User: Hello, I am John Doe.
# assistant: Hello, John! How can I assist you today?

--- Conversation Turn 2 ---
# User: What is your name?
# assistant: I'm here as your assistant, so you can just call me Assistant. How can I help you today?

--- Conversation Turn 3 ---
# User: What is my name?
# assistant: Your name is John Doe. How can I assist you today, John?

INFO:__main__:Cleaning up resources...
INFO:__main__:Thread deleted successfully
INFO:__main__:Agent deleted successfully
```

## Troubleshooting

### Common Issues

1. **Authentication Errors**: Ensure you're logged in with `az login` and have proper permissions.
2. **Missing Environment Variables**: Verify all required environment variables are set.
3. **Connection String Issues**: Ensure the Azure AI Project connection string is correct.
4. **Model Deployment Issues**: Verify the model deployment name exists and is accessible.

### Error Messages

- `Configuration error`: Missing or invalid environment variables
- `Agent initialization error`: Issues with agent creation or configuration
- `Agent invoke error`: Problems during agent execution
- `Thread operation error`: Issues with thread management

## Next Steps

After running this basic sample, you can explore:

1. **Adding Tools**: Configure the agent with custom tools and functions
2. **Streaming Responses**: Use `invoke_stream` for real-time responses
3. **Advanced Threading**: Implement more complex conversation flows
4. **Error Recovery**: Add retry logic and fallback mechanisms
5. **Integration**: Connect the agent to your applications

## Additional Resources

- [Azure AI Agent Documentation](https://learn.microsoft.com/en-us/azure/ai-services/agents/)
- [Semantic Kernel Documentation](https://learn.microsoft.com/en-us/semantic-kernel/)
- [Azure AI Project Quickstart](https://learn.microsoft.com/en-us/azure/ai-services/agents/quickstart?pivots=programming-language-python-azure)

## Azure AI Agents

The following getting started samples show how to use Azure AI Agents with Semantic Kernel.

To set up the required resources, follow the "Quickstart: Create a new agent" guide [here](https://learn.microsoft.com/en-us/azure/ai-services/agents/quickstart?pivots=programming-language-python-azure).

You will need to install the optional Semantic Kernel `azure` dependencies if you haven't already via:

```bash
pip install semantic-kernel[azure]
```

Before running an Azure AI Agent, modify your .env file to include:

```bash
AZURE_AI_AGENT_PROJECT_CONNECTION_STRING = "<example-connection-string>"
AZURE_AI_AGENT_MODEL_DEPLOYMENT_NAME = "<example-model-deployment-name>"
```

or

```bash
AZURE_AI_AGENT_MODEL_DEPLOYMENT_NAME = "<example-model-deployment-name>"
AZURE_AI_AGENT_ENDPOINT = "<example-endpoint>"
AZURE_AI_AGENT_SUBSCRIPTION_ID = "<example-subscription-id>"
AZURE_AI_AGENT_RESOURCE_GROUP_NAME = "<example-resource-group-name>"
AZURE_AI_AGENT_PROJECT_NAME = "<example-project-name>"
```

The project connection string is of the following format: `<HostName>;<AzureSubscriptionId>;<ResourceGroup>;<ProjectName>`. See [here](https://learn.microsoft.com/en-us/azure/ai-services/agents/quickstart?pivots=programming-language-python-azure#configure-and-run-an-agent) for information on obtaining the values to populate the connection string.

The .env should be placed in the root directory.

## Configuring the AI Project Client

Ensure that your Azure AI Agent resources are configured with at least a Basic or Standard SKU.

To begin, create the project client as follows:

```python
async with DefaultAzureCredential() as credential:
    client = await AzureAIAgent.create_client(credential=credential)

    async with client:
        # Your operational code here
```

### Required Imports

The required imports for the `Azure AI Agent` include async libraries:

```python
from azure.identity.aio import DefaultAzureCredential
```

### Initializing the Agent

You can pass in a connection string (shown above) to create the client:

```python
async with (
    DefaultAzureCredential() as creds,
    AzureAIAgent.create_client(
        credential=creds,
        conn_str=ai_agent_settings.project_connection_string.get_secret_value(),
    ) as client,
):
    # operational logic
```

### Creating an Agent Definition

Once the client is initialized, you can define the agent:

```python
# Create agent definition
agent_definition = await client.agents.create_agent(
    model=ai_agent_settings.model_deployment_name,
    name=AGENT_NAME,
    instructions=AGENT_INSTRUCTIONS,
)
```

Then, instantiate the `AzureAIAgent` with the `client` and `agent_definition`:

```python
# Create the AzureAI Agent
agent = AzureAIAgent(
    client=client,
    definition=agent_definition,
)
```

Now, you can create a thread, add chat messages to the agent, and invoke it with given inputs and optional parameters.

### Reusing an Agent Definition

In certain scenarios, you may prefer to reuse an existing agent definition rather than creating a new one. This can be done by calling `await client.agents.get_agent(...)` instead of `await client.agents.create_agent(...)`. 

For a practical example, refer to the [`step7_azure_ai_agent_retrieval`](./step7_azure_ai_agent_retrieval.py) sample.

## Requests and Rate Limits

### Managing API Request Frequency

Your default request limits may be low, affecting how often you can poll the status of a run. You have two options:

1. Adjust the `polling_options` of the `AzureAIAgent`

By default, the polling interval is 250 ms. You can slow it down to 1 second (or another preferred value) to reduce the number of API calls:

```python
# Required imports
from datetime import timedelta
from semantic_kernel.agents.run_polling_options import RunPollingOptions

# Configure the polling options as part of the `AzureAIAgent`
agent = AzureAIAgent(
    client=client,
    definition=agent_definition,
    polling_options=RunPollingOptions(run_polling_interval=timedelta(seconds=1)),
)
```

2. Increase Rate Limits in Azure AI Foundry

You can also adjust your deployment's Rate Limit (Tokens per minute), which impacts the Rate Limit (Requests per minute). This can be configured in Azure AI Foundry under your project's deployment settings for the "Connected Azure OpenAI Service Resource."
