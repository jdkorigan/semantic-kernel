# Simple Azure Key Vault Integration for AzureOpenAISettings
import os
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient
from semantic_kernel.connectors.ai.open_ai.settings.azure_open_ai_settings import AzureOpenAISettings

def get_azure_openai_settings_from_key_vault(key_vault_url: str) -> AzureOpenAISettings:
    """
    Retrieve Azure OpenAI settings from Azure Key Vault
    
    Args:
        key_vault_url: The URL of your Azure Key Vault (e.g., "https://your-keyvault.vault.azure.net/")
    
    Returns:
        AzureOpenAISettings: Configured settings object
    """
    try:
        # Initialize Key Vault client
        credential = DefaultAzureCredential()
        client = SecretClient(vault_url=key_vault_url, credential=credential)
        
        # Retrieve secrets from Key Vault
        api_key = client.get_secret("azure-openai-api-key").value
        endpoint = client.get_secret("azure-openai-endpoint").value
        deployment_name = client.get_secret("azure-openai-deployment-name").value
        
        # Create and return settings
        settings = AzureOpenAISettings(
            api_key=api_key,
            endpoint=endpoint,
            chat_deployment_name=deployment_name,
            api_version="2024-02-01"
        )
        
        print(f"✅ Successfully loaded settings from Key Vault:")
        print(f"   - Endpoint: {settings.endpoint}")
        print(f"   - Deployment: {settings.chat_deployment_name}")
        print(f"   - API Version: {settings.api_version}")
        
        return settings
        
    except Exception as e:
        print(f"❌ Error loading settings from Key Vault: {e}")
        raise

def get_azure_openai_settings_with_fallback(key_vault_url: str = None) -> AzureOpenAISettings:
    """
    Get Azure OpenAI settings with fallback to environment variables
    
    Args:
        key_vault_url: Optional Key Vault URL. If provided, will try Key Vault first
    
    Returns:
        AzureOpenAISettings: Configured settings object
    """
    # Try Key Vault first if URL is provided
    if key_vault_url:
        try:
            return get_azure_openai_settings_from_key_vault(key_vault_url)
        except Exception as e:
            print(f"⚠️ Key Vault failed, falling back to environment variables: {e}")
    
    # Fallback to environment variables
    print("📋 Loading settings from environment variables...")
    settings = AzureOpenAISettings()
    
    # Validate required settings
    if not settings.chat_deployment_name:
        raise ValueError("AZURE_OPENAI_CHAT_DEPLOYMENT_NAME is required")
    if not settings.endpoint:
        raise ValueError("AZURE_OPENAI_ENDPOINT is required")
    
    print(f"✅ Successfully loaded settings from environment variables:")
    print(f"   - Endpoint: {settings.endpoint}")
    print(f"   - Deployment: {settings.chat_deployment_name}")
    print(f"   - API Version: {settings.api_version}")
    
    return settings

# Example usage for your multi-agent orchestration script
def get_agents_with_key_vault(key_vault_url: str = None):
    """
    Get agents configured with Key Vault integration
    
    Args:
        key_vault_url: Optional Key Vault URL for secret management
    """
    from semantic_kernel.agents import ChatCompletionAgent
    from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion
    
    # Get settings (from Key Vault or environment variables)
    settings = get_azure_openai_settings_with_fallback(key_vault_url)
    
    # Create agents with the settings
    physics_agent = ChatCompletionAgent(
        name="PhysicsExpert",
        instructions="You are an expert in physics. You answer questions from a physics perspective.",
        service=AzureChatCompletion(
            deployment_name=settings.chat_deployment_name,
            endpoint=settings.endpoint,
            api_key=settings.api_key.get_secret_value() if settings.api_key else None,
            api_version=settings.api_version
        ),
    )
    
    chemistry_agent = ChatCompletionAgent(
        name="ChemistryExpert",
        instructions="You are an expert in chemistry. You answer questions from a chemistry perspective.",
        service=AzureChatCompletion(
            deployment_name=settings.chat_deployment_name,
            endpoint=settings.endpoint,
            api_key=settings.api_key.get_secret_value() if settings.api_key else None,
            api_version=settings.api_version
        ),
    )
    
    return [physics_agent, chemistry_agent]

# Example of how to modify your existing script
async def example_usage():
    """Example of how to use this in your existing script"""
    
    # Option 1: Use Key Vault
    # agents = get_agents_with_key_vault("https://your-keyvault.vault.azure.net/")
    
    # Option 2: Use environment variables (fallback)
    agents = get_agents_with_key_vault()
    
    return agents

if __name__ == "__main__":
    import asyncio
    asyncio.run(example_usage()) 