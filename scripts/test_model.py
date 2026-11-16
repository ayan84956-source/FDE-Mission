import json
import time
from pathlib import Path

import ollama

ROOT = Path(__file__).resolve().parent.parent
RESUME_FILE = ROOT / "sample_data" / "resumes" / "rahul_mehta.txt"

MODELS = ["llama3.2:latest", "qwen2.5-coder:3b"]
RUNS_PER_MODEL = 2

PROMPT = """You extract facts from a resume. Use ONLY information that is
written in the resume. If something is not stated, use null.
Return JSON with exactly these fields:
- "skills": list of technical skills the person already has
- "total_years_experience": number
- "location": string
- "education": string
- "job_titles": list of strings

Resume:
{resume}
"""


def extract(resume_text, model):
    start = time.time()
    response = ollama.chat(
        model=model,
        messages=[{"role": "user", "content": PROMPT.format(resume=resume_text)}],
        format="json",
        options={"temperature": 0},
        keep_alive="10m",
    )
    wall = time.time() - start

    stats = {
        "wall_s": wall,
        "load_s": response["load_duration"] / 1e9,
        "read_s": response["prompt_eval_duration"] / 1e9,
        "write_s": response["eval_duration"] / 1e9,
        "output_tokens": response["eval_count"],
    }
    stats["tokens_per_s"] = stats["output_tokens"] / stats["write_s"]

    raw = response["message"]["content"]
    try:
        return json.loads(raw), stats
    except json.JSONDecodeError:
        return {"ERROR": "broken JSON", "raw": raw}, stats


resume_text = RESUME_FILE.read_text(encoding="utf-8")

for model in MODELS:
    print(f"\n=== {model} ===")
    for run in range(1, RUNS_PER_MODEL + 1):
        result, s = extract(resume_text, model)
        print(
            f"Run {run}: total {s['wall_s']:.1f}s | load {s['load_s']:.1f}s | "
            f"read {s['read_s']:.1f}s | write {s['write_s']:.1f}s | "
            f"{s['output_tokens']} tokens at {s['tokens_per_s']:.1f} tokens/s"
        )
        if run == 1:
            print(json.dumps(result))