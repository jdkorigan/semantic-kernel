# Copyright (c) Microsoft. All rights reserved.

import asyncio
import os

script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)

from dotenv import load_dotenv

from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion
from semantic_kernel.connectors.ai.open_ai.prompt_execution_settings.azure_chat_prompt_execution_settings import AzureChatPromptExecutionSettings
from semantic_kernel.contents import ChatMessageContent
from semantic_kernel.contents.image_content import ImageContent
from semantic_kernel.contents.text_content import TextContent
from semantic_kernel.contents.utils.author_role import AuthorRole
from semantic_kernel.contents.chat_history import ChatHistory

"""
The following sample demonstrates how to create an Azure OpenAI Chat Completion service for vision tasks.
The sample shows how to have the service answer questions about the provided images.

This version uses the Chat Completion API which supports vision capabilities with GPT-4o.
"""


async def main():
    load_dotenv()

    deployment_name = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")

    # 1. Create the Azure OpenAI chat completion service
    chat_service = AzureChatCompletion(
        service_id="azure_chat",
        deployment_name=deployment_name,
        endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
        api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    )

    # 2. Define a file path for an image that will be used in the conversation
    file_path = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), "resources", "cat.jpg")

    # 3. Define a list of user messages that include text and image content for the vision task
    user_messages = [
        ChatMessageContent(
            role=AuthorRole.USER,
            items=[
                TextContent(text="Describe this image."),
                ImageContent(
                    uri="https://upload.wikimedia.org/wikipedia/commons/thumb/4/47/New_york_times_square-terabass.jpg/1200px-New_york_times_square-terabass.jpg"
                ),
            ],
        ),
        ChatMessageContent( 
            role=AuthorRole.USER,
            items=[
                TextContent(text="What is the main color in this image?"),
                ImageContent(uri="https://upload.wikimedia.org/wikipedia/commons/5/56/White_shark.jpg"),
            ],
        ),
        ChatMessageContent(
            role=AuthorRole.USER,
            items=[
                TextContent(text="Is there an animal in this image?"),
                ImageContent.from_image_file(file_path),
            ],
        ),
    ]

    # 4. Process each message
    for i, user_input in enumerate(user_messages):
        print(f"# User: {str(user_input)}")  # type: ignore
        
        try:
            # 5. Create a chat history with the user message
            chat_history = ChatHistory()
            chat_history.add_message(user_input)
            
            # 6. Create settings for the chat completion
            settings = AzureChatPromptExecutionSettings(
                ai_model_id=deployment_name,
                temperature=0.7,
                max_tokens=1000
            )
            
            # 7. Get the response from the chat service
            response = await chat_service.get_chat_message_contents(chat_history, settings=settings)
            
            if response and len(response) > 0:
                print(f"# Assistant: {response[0].content}\n")
            else:
                print("No response received\n")
                
        except Exception as e:
            print(f"Error processing message {i+1}: {e}")
            print("Continuing with next message...")
            continue

    """
    You should see output similar to the following:

    # User: Describe this image.
    # Assistant: The image depicts a bustling scene of Times Square in New York City...

    # User: What is the main color in this image?
    # Assistant: The main color in the image is blue.

    # User: Is there an animal in this image?
    # Assistant: Yes, there is a cat in the image.
     """


if __name__ == "__main__":
    asyncio.run(main())
