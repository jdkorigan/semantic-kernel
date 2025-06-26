# Copyright (c) Microsoft. All rights reserved.
"""
Test script to debug Azure AI Agent configuration.
This script helps identify configuration issues before running the main sample.
"""

from dotenv import load_dotenv
load_dotenv()

import os
import sys

def test_configuration():
    """Test the Azure AI Agent configuration."""
    print("=== Azure AI Agent Configuration Test ===\n")
    
    # Check for Azure-related environment variables
    azure_vars = {k: v for k, v in os.environ.items() if 'AZURE' in k}
    
    print("Found Azure-related environment variables:")
    for key, value in azure_vars.items():
        # Mask sensitive values
        if 'CONNECTION_STRING' in key or 'KEY' in key:
            masked_value = value[:10] + "..." if value else "None"
        else:
            masked_value = value
        print(f"  {key}: {masked_value}")
    
    print("\nRequired variables check:")
    
    # Check required variables
    required_vars = [
        "AZURE_AI_AGENT_MODEL_DEPLOYMENT_NAME",
        "AZURE_AI_AGENT_PROJECT_CONNECTION_STRING"
    ]
    
    missing_vars = []
    for var in required_vars:
        if var in os.environ and os.environ[var]:
            print(f"  ✓ {var}: Set")
        else:
            print(f"  ✗ {var}: Missing or empty")
            missing_vars.append(var)
    
    if missing_vars:
        print(f"\n❌ Configuration incomplete. Missing: {', '.join(missing_vars)}")
        print("\nTo fix this:")
        print("1. Create a .env file in this directory")
        print("2. Add the missing environment variables")
        print("3. See env_example.txt for the correct format")
        return False
    else:
        print("\n✅ All required variables are set!")
        
        # Try to import and test AzureAIAgentSettings
        try:
            from semantic_kernel.agents import AzureAIAgentSettings
            settings = AzureAIAgentSettings()
            print(f"✅ Successfully loaded AzureAIAgentSettings")
            print(f"   Model deployment name: {settings.model_deployment_name}")
            print(f"   Project connection string: {'Set' if settings.project_connection_string else 'Not set'}")
            return True
        except Exception as e:
            print(f"❌ Failed to load AzureAIAgentSettings: {e}")
            return False

if __name__ == "__main__":
    success = test_configuration()
    sys.exit(0 if success else 1) 