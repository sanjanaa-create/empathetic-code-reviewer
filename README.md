# Empathetic Code Reviewer 🤝

A tool that takes a code snippet and direct/critical review comments, then rewrites them into empathetic, constructive, and educational feedback — like an ideal senior developer would give.

## 🚀 Features

* Rephrases harsh review comments into supportive, actionable suggestions.
* Explains not just what to change, but also why.
* Provides improved code examples following Python best practices (PEP 8).
* Supports two modes:

  * AI Mode: Uses OpenAI GPT-4o-mini for natural feedback (requires API key & credits).
  * Mock Mode: Fallback for offline/demo (prebuilt rules ensure it still works).

## 📂 Project Structure

* main.py → Core program
* input.json → Example input
* report.md → Example output (generated)
* requirements.txt → Python dependencies

## 🛠 Setup & Run (Windows PowerShell)

1. Clone the repo:
   git clone [https://github.com/YOUR-USERNAME/empathetic-code-reviewer.git](https://github.com/YOUR-USERNAME/empathetic-code-reviewer.git)
   cd empathetic-code-reviewer

2. Create virtual environment & activate:
   python -m venv .venv
   ..venv\Scripts\Activate.ps1

3. Install dependencies:
   pip install -r requirements.txt

4. (Optional) Set OpenAI API Key for AI mode:
   \$env\:OPENAI\_API\_KEY="sk-yourkeyhere"

5. Run the program:
   python main.py --in input.json --out report.md

* If API key & credits available → AI mode
* If not → falls back to Mock mode (still works)

## 📊 Example

Input (input.json):
{
"code\_snippet": "def get\_active\_users(users):\n  results = \[]\n  for u in users:\n    if u.is\_active == True and u.profile\_complete == True:\n      results.append(u)\n  return results",
"review\_comments": \[
"This is inefficient. Don't loop twice conceptually.",
"Variable 'u' is a bad name.",
"Boolean comparison '== True' is redundant."
]
}

Output (report.md):

* Positive rephrasing
* Explanation of why
* Suggested improved code
* Summary of improvements

## 👩‍⚖️ Hackathon Notes

* Judges can run the project with or without API credits.
* With credits → real AI (GPT-4o-mini).
* Without credits → Mock mode ensures working demo.

## 👩‍💻 Author

Built by Sanjana for Hackathon 2025 🚀
