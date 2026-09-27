import os
import json
import base64
import io
from PIL import Image, ImageChops
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import WebDriverException, TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import google.generativeai as genai
from dotenv import load_dotenv
import pdfkit

from .models import TestCase 
from . import db

load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

def compare_images(base64_img1, base64_img2):
    img1_data = base64.b64decode(base64_img1)
    img2_data = base64.b64decode(base64_img2)
    img1 = Image.open(io.BytesIO(img1_data))
    img2 = Image.open(io.BytesIO(img2_data))
    if img1.size != img2.size: return 100.0, None
    diff = ImageChops.difference(img1.convert('RGB'), img2.convert('RGB'))
    if not diff.getbbox(): return 0.0, None
    num_diff_pixels = sum(1 for pixel in diff.getdata() if any(val > 32 for val in pixel))
    total_pixels = img1.size[0] * img1.size[1]
    diff_percentage = (num_diff_pixels / total_pixels) * 100
    diff_image_bytes = io.BytesIO()
    diff.save(diff_image_bytes, format='PNG')
    diff_base64 = base64.b64encode(diff_image_bytes.getvalue()).decode('utf-8')
    return diff_percentage, diff_base64

def translate_natural_language_to_command(natural_command):
    if not os.getenv("GOOGLE_API_KEY"):
        return "Error: GOOGLE_API_KEY not configured."
    try:
        model = genai.GenerativeModel('models/gemini-2.5-pro')
        prompt = f"""
        Analyze the following natural language command and convert it into the strict, machine-readable format for a web automation tool.
        The ONLY valid output commands are:
        1. type "text" into "selector=value"
        2. click "selector=value"
        3. verify text "text" in "selector=value"
        - For login fields, assume email is "id=email" and password is "id=pass".
        - For a login button, assume "name=login".
        - Be precise. Only output the command(s).
        User Command: "{natural_command}"
        Your Output:
        """
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"Error: Could not translate command. Details: {e}"

def get_ai_bug_suggestion(error_message, url, command):
    if not os.getenv("GOOGLE_API_KEY"):
        return "AI analysis skipped. GOOGLE_API_KEY not configured."
    try:
        model = genai.GenerativeModel('models/gemini-2.5-pro')
        prompt = f"""
        Analyze the following Selenium automation test failure. 
        Provide a concise analysis with a "Probable Cause" and a "Suggested Fix".

        - Website URL: {url}
        - Test Command: "{command}"
        - Error Message: "{error_message}"

        Analysis:
        """
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Could not get AI suggestion. Error: {e}"

def generate_script_from_goal(url, goal):
    try:
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('--window-size=1280,800')
        driver = webdriver.Chrome(options=options)
        driver.get(url)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        html_content = driver.page_source
        driver.quit()

        model = genai.GenerativeModel('models/gemini-2.5-pro')
        prompt = f"""
        As a senior QA automation engineer, your task is to write a test script based on a user's goal and the HTML of a webpage.
        The ONLY valid commands you can use are:
        1. type "text" into "selector=value"
        2. click "selector=value"
        3. verify text "text" in "selector=value"
        RULES:
        - Analyze the user's goal and the provided HTML.
        - Find the most reliable selectors for the elements needed to achieve the goal (e.g., 'id', 'data-test', 'name').
        - For selectors, use 'id=', 'name=', 'class_name=', 'css_selector=', or 'xpath='.
        - If the goal mentions placeholders like MY_EMAIL, use them in the script.
        - Do not add any comments or explanations. Only output the raw command script.
        USER GOAL: "{goal}"
        WEBPAGE HTML:
        ---
        {html_content[:15000]} 
        ---
        Based on the goal and the HTML, generate the test script:
        """
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"# An error occurred during script generation:\n# {e}"

def run_test(url, commands_text, test_case_id=None, is_visual_test=False):
    test_results = []
    baseline_images = {}
    if is_visual_test and test_case_id:
        test_case = TestCase.query.get(test_case_id)
        if test_case and test_case.baseline_images_json:
            baseline_images = json.loads(test_case.baseline_images_json)

    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--window-size=1280,800')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    
    try:
        driver = webdriver.Chrome(options=options)
    except Exception as e:
         return [{"step": "Setup", "command": "Initialize WebDriver", "status": "Failed", "details": f"Could not start Chrome. Error: {e}"}]

    driver.get(url)
    commands = [cmd.strip() for cmd in commands_text.split('\n') if cmd.strip()]
    for i, command in enumerate(commands):
        step_result = {"step": i + 1, "command": command, "status": "Failed", "details": "Unknown command"}
        try:
            wait = WebDriverWait(driver, 10)
            parts = command.lower().split()
            action = parts[0]
            if action == "type":
                text_to_type = command.split('"')[1]
                selector_part = command.split('into "')[1].replace('"', '')
                by, value = selector_part.split('=', 1)
                locator = (getattr(By, by.upper()), value)
                element = wait.until(EC.presence_of_element_located(locator))
                element.clear()
                element.send_keys(text_to_type)
                step_result["status"] = "Success"
                step_result["details"] = f"Typed '{text_to_type}' into element '{value}'."
            elif action == "click":
                selector_part = command.split('"')[1]
                by, value = selector_part.split('=', 1)
                locator = (getattr(By, by.upper()), value)
                element = wait.until(EC.element_to_be_clickable(locator))
                element.click()
                step_result["status"] = "Success"
                step_result["details"] = f"Clicked element '{value}'."
            elif action == "jsclick":
                selector_part = command.split('"')[1]
                by, value = selector_part.split('=', 1)
                locator = (getattr(By, by.upper()), value)
                element = wait.until(EC.presence_of_element_located(locator))
                driver.execute_script("arguments[0].click();", element)
                step_result["status"] = "Success"
                step_result["details"] = f"Clicked element '{value}' using JavaScript."
            elif action == "verify":
                text_to_verify = command.split('"')[1]
                selector_part = command.split('in "')[1].replace('"', '')
                by, value = selector_part.split('=', 1)
                locator = (getattr(By, by.upper()), value)
                wait.until(EC.text_to_be_present_in_element(locator, text_to_verify))
                step_result["status"] = "Success"
                step_result["details"] = f"Found text '{text_to_verify}' in element '{value}'."
            else:
                step_result["details"] = f"Command '{action}' is not supported."
            
            if is_visual_test:
                new_screenshot = driver.get_screenshot_as_base64()
                step_key = str(i + 1)
                baseline_screenshot = baseline_images.get(step_key)
                if baseline_screenshot:
                    diff_percent, diff_image = compare_images(baseline_screenshot, new_screenshot)
                    if diff_percent > 0.1:
                        step_result['status'] = 'Visual Mismatch'
                        step_result['details'] = f"Visual difference of {diff_percent:.2f}% detected."
                        step_result['screenshot'] = diff_image
                    else:
                        step_result['details'] += " (Visuals Match)"
                        step_result['screenshot'] = new_screenshot
                else:
                    step_result['status'] = 'New Baseline'
                    step_result['details'] = "No baseline found for this step. Approve to save."
                    step_result['screenshot'] = new_screenshot
        
        except TimeoutException:
            error_details = f"Element or text not found within 10 seconds"
            step_result["details"] = f"Error: {error_details}"
            step_result["ai_suggestion"] = get_ai_bug_suggestion(error_details, url, command)
        except WebDriverException as e:
            error_details = str(e).split('\n')[0]
            step_result["details"] = f"Error: {error_details}"
            step_result["ai_suggestion"] = get_ai_bug_suggestion(error_details, url, command)
        except Exception as e:
            step_result["details"] = f"An unexpected error occurred: {e}"
        
        test_results.append(step_result)
        if step_result["status"] in ["Failed", "Visual Mismatch"]:
            break
    driver.quit()
    return test_results

def analyze_code_for_bugs(code_to_analyze):
    """Uses AI to review a block of code and find potential bugs."""
    try:
        model = genai.GenerativeModel('models/gemini-2.5-pro')
        prompt = f"""
        As an expert senior software developer and code reviewer, your task is to analyze the following Python code for potential issues.
        Please review the code for:
        1.  **Bugs or Logical Errors:** Identify any code that will not work as intended.
        2.  **Security Vulnerabilities:** Look for common vulnerabilities (e.g., SQL injection, hardcoded secrets).
        3.  **Performance Issues:** Point out any inefficient code.
        4.  **Best Practice Violations:** Suggest improvements based on standard Python best practices (PEP 8).
        Provide a clear, concise report. For each issue found, describe the problem and suggest a corrected version of the code. If no issues are found, state that the code looks good.
        CODE TO ANALYZE:
        ---
        {code_to_analyze}
        ---
        ANALYSIS REPORT:
        """
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"# An error occurred during code analysis:\n# {e}"

def generate_unit_tests(code_to_analyze):
    """Uses AI to generate a pytest unit test suite for a given function."""
    try:
        model = genai.GenerativeModel('models/gemini-2.5-pro')
        prompt = f"""
        As a senior QA automation engineer, your task is to write a comprehensive unit test suite for the provided Python function using the `pytest` framework.
        RULES:
        - Import the `pytest` library.
        - For the function provided, create test cases that cover:
          1. The "happy path" with typical, valid inputs.
          2. Edge cases (e.g., empty strings, zeros, negative numbers).
          3. Error conditions (e.g., invalid input types). Use `pytest.raises` for this.
        - The generated code should be a complete, runnable Python script.
        - Do not add any conversational text or explanations outside of the code comments.
        PYTHON FUNCTION TO TEST:
        ---
        {code_to_analyze}
        ---
        PYTEST UNIT TEST SCRIPT:
        """
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"# An error occurred during unit test generation:\n# {e}"
    
def refactor_code(code_to_analyze):
    """Uses AI to refactor a block of code."""
    try:
        model = genai.GenerativeModel('models/gemini-2.5-pro')
        prompt = f"""
        As a senior Python developer, refactor the following code to improve its readability, efficiency, and adherence to best practices (PEP 8), without changing its core functionality.

        Provide the refactored code inside a Python code block, followed by a brief, bulleted list explaining the key changes you made.

        ORIGINAL CODE:
        ---
        {code_to_analyze}
        ---

        REFACTORED CODE AND EXPLANATION:
        """
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"# An error occurred during code refactoring:\n# {e}"