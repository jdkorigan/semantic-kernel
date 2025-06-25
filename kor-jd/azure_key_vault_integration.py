# Azure Key Vault Integration with AzureOpenAISettings
import os
import asyncio
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient
from semantic_kernel.connectors.ai.open_ai.settings.azure_open_ai_settings import AzureOpenAISettings
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion
from semantic_kernel.connectors.ai.open_ai import OpenAIChatCompletion
from semantic_kernel import Kernel
from semantic_kernel.plugins.core import OpenApiPlugin
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion

class AzureKeyVaultSettings:
    """Helper class to manage Azure Key Vault integration"""
    
    def __init__(self, vault_url: str):
        self.vault_url = vault_url
        self.credential = DefaultAzureCredential()
        self.client = SecretClient(vault_url=vault_url, credential=self.credential)
    
    def get_secret(self, secret_name: str) -> str:
        """Retrieve a secret from Azure Key Vault"""
        try:
            secret = self.client.get_secret(secret_name)
            return secret.value
        except Exception as e:
            print(f"Error retrieving secret {secret_name}: {e}")
            return None

# Method 1: Manual Key Vault Integration
async def method1_manual_key_vault():
    """Manually retrieve secrets from Key Vault and use them with AzureOpenAISettings"""
    
    # Initialize Key Vault client
    key_vault = AzureKeyVaultSettings("https://your-keyvault.vault.azure.net/")
    
    # Retrieve secrets from Key Vault
    api_key = key_vault.get_secret("azure-openai-api-key")
    endpoint = key_vault.get_secret("azure-openai-endpoint")
    deployment_name = key_vault.get_secret("azure-openai-deployment-name")
    
    # Create settings with Key Vault values
    settings = AzureOpenAISettings(
        api_key=api_key,
        endpoint=endpoint,
        chat_deployment_name=deployment_name,
        api_version="2024-02-01"
    )
    
    # Use settings to create AzureChatCompletion
    chat_completion = AzureChatCompletion(
        deployment_name=settings.chat_deployment_name,
        endpoint=settings.endpoint,
        api_key=settings.api_key.get_secret_value() if settings.api_key else None,
        api_version=settings.api_version
    )
    
    return chat_completion

# Method 2: Environment Variables with Key Vault References
async def method2_env_with_key_vault():
    """Use environment variables that reference Key Vault secrets"""
    
    # Set environment variables to Key Vault references
    # These would be set in your deployment configuration
    os.environ["AZURE_OPENAI_API_KEY"] = "@Microsoft.KeyVault(SecretUri=https://your-keyvault.vault.azure.net/secrets/azure-openai-api-key/)"
    os.environ["AZURE_OPENAI_ENDPOINT"] = "https://your-resource.openai.azure.com/"
    os.environ["AZURE_OPENAI_CHAT_DEPLOYMENT_NAME"] = "your-deployment-name"
    
    # AzureOpenAISettings will automatically read from environment variables
    settings = AzureOpenAISettings()
    
    # Validate settings
    if not settings.chat_deployment_name:
        raise ValueError("AZURE_OPENAI_CHAT_DEPLOYMENT_NAME is required")
    if not settings.endpoint:
        raise ValueError("AZURE_OPENAI_ENDPOINT is required")
    
    # Create chat completion service
    chat_completion = AzureChatCompletion(
        deployment_name=settings.chat_deployment_name,
        endpoint=settings.endpoint,
        api_key=settings.api_key.get_secret_value() if settings.api_key else None,
        api_version=settings.api_version
    )
    
    return chat_completion

# Method 3: Using Azure Key Vault Plugin
async def method3_key_vault_plugin():
    """Use the Azure Key Vault plugin with Semantic Kernel"""
    
    # Create kernel
    kernel = Kernel()
    
    # Add Azure OpenAI service (secrets will be retrieved from Key Vault)
    kernel.add_service(AzureChatCompletion(
        deployment_name="your-deployment-name",
        endpoint="https://your-resource.openai.azure.com/",
        # The API key will be retrieved from Key Vault automatically
        # when using DefaultAzureCredential
    ))
    
    # Import the Azure Key Vault plugin
    # This requires the OpenAPI specification for Azure Key Vault
    key_vault_plugin = kernel.import_plugin_from_openapi(
        plugin_name="AzureKeyVault",
        openapi_document_path="path/to/azure-key-vault-openapi.yaml",
        execution_settings=None
    )
    
    return kernel, key_vault_plugin

# Method 4: Custom Settings Class with Key Vault
class AzureOpenAISettingsWithKeyVault(AzureOpenAISettings):
    """Extended AzureOpenAISettings that can retrieve secrets from Key Vault"""
    
    def __init__(self, key_vault_url: str = None, **kwargs):
        super().__init__(**kwargs)
        
        if key_vault_url:
            self.key_vault = AzureKeyVaultSettings(key_vault_url)
            self._load_secrets_from_key_vault()
    
    def _load_secrets_from_key_vault(self):
        """Load secrets from Key Vault if not already set"""
        if not self.api_key:
            api_key = self.key_vault.get_secret("azure-openai-api-key")
            if api_key:
                from pydantic import SecretStr
                self.api_key = SecretStr(api_key)
        
        if not self.endpoint:
            endpoint = self.key_vault.get_secret("azure-openai-endpoint")
            if endpoint:
                self.endpoint = endpoint
        
        if not self.chat_deployment_name:
            deployment_name = self.key_vault.get_secret("azure-openai-deployment-name")
            if deployment_name:
                self.chat_deployment_name = deployment_name

# Example usage
async def main():
    print("=== Method 1: Manual Key Vault Integration ===")
    try:
        chat_completion1 = await method1_manual_key_vault()
        print("✅ Method 1: Successfully created chat completion with manual Key Vault integration")
    except Exception as e:
        print(f"❌ Method 1 failed: {e}")
    
    print("\n=== Method 2: Environment Variables with Key Vault ===")
    try:
        chat_completion2 = await method2_env_with_key_vault()
        print("✅ Method 2: Successfully created chat completion with environment variables")
    except Exception as e:
        print(f"❌ Method 2 failed: {e}")
    
    print("\n=== Method 3: Key Vault Plugin ===")
    try:
        kernel, plugin = await method3_key_vault_plugin()
        print("✅ Method 3: Successfully created kernel with Key Vault plugin")
    except Exception as e:
        print(f"❌ Method 3 failed: {e}")
    
    print("\n=== Method 4: Custom Settings Class ===")
    try:
        settings = AzureOpenAISettingsWithKeyVault(
            key_vault_url="https://your-keyvault.vault.azure.net/"
        )
        print("✅ Method 4: Successfully created custom settings with Key Vault integration")
    except Exception as e:
        print(f"❌ Method 4 failed: {e}")

if __name__ == "__main__":
    asyncio.run(main()) 