import os
import google.generativeai as genai
from dotenv import load_dotenv

# This loads your API key from the .env file
load_dotenv()
try:
    genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

    print("--- Finding available models for your API key ---")
    
    found_models = False
    for m in genai.list_models():
      # We are looking for models that can be used for our purpose
      if 'generateContent' in m.supported_generation_methods:
        print(f"Found model: {m.name}")
        found_models = True
        
    if not found_models:
        print("\nNo models supporting 'generateContent' were found. Please check your API key and project settings in Google AI Studio.")

except Exception as e:
    print(f"\nAn error occurred. Please ensure your GOOGLE_API_KEY in the .env file is correct.\nDetails: {e}")