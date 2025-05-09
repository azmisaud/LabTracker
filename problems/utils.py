import os
from dotenv import load_dotenv

load_dotenv()

api_key=os.getenv("GEMINI_API_KEY")

import google.generativeai as genai
import re

# Configure the Google Generative AI client with your API key
genai.configure(api_key=api_key)

# Initialize the Gemini 2.0 Flash model
model = genai.GenerativeModel("gemini-2.0-flash")

def analyze_code_with_ai(code, problem_description):
    if not code.strip():
        return "No code submitted."

    prompt = (
        f"You are an expert code reviewer.\n"
        f"Given the following problem and code, provide a concise and precise analysis.\n\n"
        f"Problem Description:\n{problem_description}\n\n"
        f"Code:\n{code}\n\n"
        f"Answer the following:\n"
        f"1. What does the code do? What lan\n"
        f"2. Does it solve the problem correctly?\n"
        f"Keep the response short and clear. Do not repeat the code or problem description.\n"
    )

    try:
        # Generate the response using Google Generative AI
        response = model.generate_content(prompt)
        result = response.text.strip()

        # Match both answers using regex
        match = re.search(r"1\.\s*(.+?)\s*2\.\s*(.+)", result, re.DOTALL)
        if match:
            answer_1 = match.group(1).strip()
            answer_2 = match.group(2).strip()
            return f"1. {answer_1}\n\n2. {answer_2}"
        else:
            return f"AI response format not recognized:\n\n{result}"

    except Exception as e:
        return f"Gemini API error: {e}"
