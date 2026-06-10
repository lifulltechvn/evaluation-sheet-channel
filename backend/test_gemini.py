"""Quick test for Gemini via Vertex AI."""

import os
from google import genai
from google.genai.types import HttpOptions

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "credentials.json"

client = genai.Client(
    http_options=HttpOptions(api_version="v1"),
    vertexai=True,
    project="lftv-ai-contest-channel",
    location="asia-southeast1",
)

response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents="Do you know AWS?",
)

print("✅ Gemini (Vertex AI) connected successfully!")
print("Response:", response.text)
