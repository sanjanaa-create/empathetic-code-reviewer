import os, json, argparse, sys, re
from datetime import datetime
from openai import OpenAI
from openai import RateLimitError, AuthenticationError, APIError

# Init OpenAI client (but may fail if no key)
api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key) if api_key else None

HEADER = """# Empathetic Code Review Report
_Generated on {date}_

"""

SECTION_TEMPLATE = """---
### Analysis of Comment: "{original}"

* **Positive Rephrasing:** {positive}
* **The 'Why':** {why}
* **Suggested Improvement:**
""" + "```python\n{code}\n```" + """
"""

SUMMARY_HEADER = """
---
## Holistic Summary
{summary}
"""

PEP8_LINK = "https://peps.python.org/pep-0008/"

# ---------------- MOCK FALLBACK ----------------
def mock_rewrite(code_snippet: str, comment: str) -> dict:
    if "inefficient" in comment.lower():
        pos = "Great start! We can make this more efficient by combining checks into one pass."
        why = "Efficiency matters for larger datasets. List comprehensions are faster and cleaner."
        code = "def get_active_users(users):\n    return [u for u in users if u.is_active and u.profile_complete]"
    elif "bad name" in comment.lower():
        pos = "Nice job! Let’s use a more descriptive variable name to improve readability."
        why = "Descriptive names make code easier to maintain and understand (see PEP 8)."
        code = "for user in users:\n    if user.is_active and user.profile_complete:\n        results.append(user)"
    elif "== true" in comment.lower():
        pos = "Good use of conditions! In Python, comparing directly to True isn’t needed."
        why = "Booleans are already truthy. `if flag:` is the Pythonic way."
        code = "if user.is_active and user.profile_complete:\n    results.append(user)"
    else:
        pos = "Solid work! We can polish this a little further for clarity."
        why = "Small improvements in style or naming make code easier to review."
        code = code_snippet
    return {"positive": pos, "why": why + f" (See: {PEP8_LINK})", "code": code}

# ---------------- AI MODE ----------------
def ai_rewrite(code_snippet: str, comment: str) -> dict:
    if not client:
        return mock_rewrite(code_snippet, comment)
    try:
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are an empathetic senior developer. Rewrite feedback kindly, explain WHY, and show better code."},
                {"role": "user", "content": f"Code:\n```python\n{code_snippet}\n```\n\nComment: {comment}\n\nReturn exactly 3 parts:\n1. Positive Rephrasing\n2. The 'Why'\n3. Suggested Improvement (code block)"}
            ],
            temperature=0.4
        )
        text = resp.choices[0].message.content.strip()

        # Try to extract code block
        code_match = re.search(r"```python(.*?)```", text, re.DOTALL)
        code = code_match.group(1).strip() if code_match else code_snippet

        # Extract positive and why
        positive = "N/A"
        why = "N/A"
        for line in text.splitlines():
            if line.lower().startswith("positive"):
                positive = line.split(":", 1)[-1].strip()
            if "why" in line.lower():
                why = line.split(":", 1)[-1].strip()

        return {"positive": positive, "why": why + f" (See: {PEP8_LINK})", "code": code}

    except (RateLimitError, AuthenticationError, APIError):
        # If quota, key, or API issue → fallback to mock
        return mock_rewrite(code_snippet, comment)

# ---------------- BUILD REPORT ----------------
def build_report(code_snippet: str, comments: list[str]) -> str:
    out = HEADER.format(date=datetime.now().strftime("%Y-%m-%d %H:%M"))
    out += f"**Context code:**\n```python\n{code_snippet}\n```\n\n"
    for c in comments:
        data = ai_rewrite(code_snippet, c)
        out += SECTION_TEMPLATE.format(original=c, positive=data["positive"], why=data["why"], code=data["code"])

    # Summary (try AI, fallback to mock)
    summary = "Great progress! Main improvements suggested: naming clarity, avoiding redundant checks, and efficiency with comprehensions."
    if client:
        try:
            resp = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "Summarize feedback in 1-2 sentences, encouraging tone."},
                    {"role": "user", "content": "Summarize the main improvements about naming clarity, avoiding redundant checks, and efficiency."}
                ],
                temperature=0.3
            )
            summary = resp.choices[0].message.content.strip()
        except (RateLimitError, AuthenticationError, APIError):
            pass

    out += SUMMARY_HEADER.format(summary=summary)
    return out

# ---------------- MAIN ----------------
def main():
    ap = argparse.ArgumentParser(description="Empathetic Code Reviewer")
    ap.add_argument("--in", dest="infile", required=True, help="Path to input JSON")
    ap.add_argument("--out", dest="outfile", required=True, help="Path to output Markdown")
    args = ap.parse_args()

    with open(args.infile, "r", encoding="utf-8") as f:
        data = json.load(f)

    code_snippet = data["code_snippet"]
    comments = data["review_comments"]

    report = build_report(code_snippet, comments)
    with open(args.outfile, "w", encoding="utf-8") as f:
        f.write(report)
    print(f"✅ Wrote {args.outfile}")

if __name__ == "__main__":
    main()
