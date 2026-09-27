# AI Powered Automation Testing TestVerse
Final year MCA project: An AI-powered web application for software testing, integrating Flask, Selenium, and the Google Gemini API.

# Prem TestVerse - An AI-Powered Automation Testing Platform

![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python)
![Flask](https://img.shields.io/badge/Flask-black?logo=flask)
![Selenium](https://img.shields.io/badge/Selenium-43B02A?logo=selenium)
![License](https://img.shields.io/badge/License-MIT-green)

An advanced, full-stack web application designed for a final year MCA project. Prem TestVerse demonstrates the powerful integration of Artificial Intelligence with both black-box and white-box software testing methodologies.

---

###  Main Dashboard

<img width="1897" height="895" alt="image" src="https://github.com/user-attachments/assets/10abc650-25eb-49c2-aea9-e95d63579ded" />


---

## 🚀 Core Features

This project is a comprehensive testing platform with a rich set of features:

#### **Black-Box Testing Suite**
* **AI Script Generation:** Generate complete Selenium test scripts by providing a URL and a high-level goal in plain English.
* **Natural Language Translation:** Write step-by-step test commands in simple English and have the AI translate them into the structured command format.
* **Multi-Language Voice Commands:** Execute tests hands-free by speaking commands in multiple languages, including English, Hindi, and Marathi.
* **Visual Regression Testing:** Save "baseline" screenshots of your application and automatically detect any unintended visual changes on future test runs.

#### **White-Box Testing Suite**
* **AI Code Reviewer:** Paste Python code and get an instant analysis from the AI, which checks for bugs, security vulnerabilities, performance issues, and best practice violations.
* **AI Unit Test Generator:** Automatically generate a complete `pytest` unit test suite for any given Python function.
* **AI Code Refactoring:** Clean up messy or inefficient code with a single click.

#### **Workflow & Reporting**
* **AI Bug Assistant:** When a test fails, the AI analyzes the error and provides a "Probable Cause" and a "Suggested Fix," dramatically reducing debugging time.
* **Persistent Test History:** All test runs are saved to your user account for later review.
* **Save & Re-run Test Suites:** Save complex test scripts as named "Test Suites" and re-run them anytime with a single click.
* **Professional PDF & Excel Reports:** Download beautifully formatted PDF or Excel reports for both black-box test runs and white-box code analysis.
* **CI/CD Deployment:** The application is fully configured for Continuous Integration and Deployment using a `Dockerfile` and is deployed on a live cloud platform.

---

## 🛠️ Tech Stack

* **Backend:** Python, Flask, Flask-SQLAlchemy, Flask-Login
* **Frontend:** HTML, CSS, Bootstrap 5, JavaScript
* **Automation:** Selenium
* **AI Integration:** Google Gemini API
* **Image Processing:** Pillow
* **Reporting:** FPDF2 (for black-box PDFs), PDFKit (for white-box PDFs), OpenPyXL (for Excel)
* **Deployment:** Docker, Gunicorn, Render

---

## ⚙️ Local Setup

To run this project on your local machine:

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/YOUR_USERNAME/YOUR_REPOSITORY.git](https://github.com/YOUR_USERNAME/YOUR_REPOSITORY.git)
    cd YOUR_REPOSITORY
    ```
2.  **Create a virtual environment:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```
3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
4.  **Set up environment variables:**
    * Create a file named `.env` in the root directory.
    * Add your secret keys to this file:
        ```
        GOOGLE_API_KEY=your_google_api_key_here
        SECRET_KEY=a_long_random_secret_string
        ```
5.  **Run the application:**
    ```bash
    python run.py
    ```
    The application will be available at `http://127.0.0.1:5000`.

---

## ✨ Feature Spotlights

### AI Script Generation & Bug Assistance
<img width="1917" height="839" alt="image" src="https://github.com/user-attachments/assets/bfb8d95a-26ee-4972-ba54-8aeb298faa2c" />
<img width="1896" height="518" alt="image" src="https://github.com/user-attachments/assets/d4446e3d-1917-487d-a00f-c9720ba650bc" />

### Test Result
<img width="1659" height="431" alt="image" src="https://github.com/user-attachments/assets/b717baae-a539-4d7e-a85a-d637440959b0" />

### PDF Report
<img width="1883" height="903" alt="image" src="https://github.com/user-attachments/assets/f8709b8d-2acb-4471-977c-176dfb313ea8" />

### Visual Regression Testing
<img width="1627" height="898" alt="image" src="https://github.com/user-attachments/assets/0c52e8b5-fdf2-4c47-8fce-57e4dc295212" />


### White-Box Code Analysis
<img width="1896" height="900" alt="Screenshot 2025-10-10 195313" src="https://github.com/user-attachments/assets/a0233b9c-b680-439f-9a85-3ff685a7749e" />


### Professional PDF Report
<img width="1905" height="898" alt="image" src="https://github.com/user-attachments/assets/f8e309ca-4665-4db7-830e-d5df1f031879" />
