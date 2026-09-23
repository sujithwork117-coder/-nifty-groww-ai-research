roq Integration for the NIFTY Research Agent

Goal

Use the official Groq Python SDK as the LLM provider for the
research agent running in GitHub Codespaces.

Official Groq documentation: -
https://console.groq.com/docs/quickstart -
https://console.groq.com/docs/libraries -
https://console.groq.com/docs/api-reference -
https://console.groq.com/docs/openai

1. API key

Use the environment variable:

GROQ_API_KEY

Never: - hard-code the key - store it in the repository - read it from
llmkey.md - print it - put it in logs or reports - commit it to Git -
ask the user to paste it into chat

The official Groq quickstart recommends GROQ_API_KEY as an environment
variable.

Example:

export GROQ_API_KEY="YOUR_KEY"

The real key must never appear in source code or this document.

2. GitHub Codespaces

The key should be configured as a GitHub Codespaces secret named:

GROQ_API_KEY

Inside the Codespace, verify only that it exists:

python -c 'import os; print("GROQ_API_KEY_PRESENT=", bool(os.getenv("GROQ_API_KEY")))'

Expected:

GROQ_API_KEY_PRESENT= True

Never print the actual value.

3. Official Python SDK

Install:

pip install groq

Use:

import os
from groq import Groq

api_key = os.environ.get("GROQ_API_KEY")

if not api_key:
    raise RuntimeError("Missing GROQ_API_KEY in environment")

client = Groq(api_key=api_key)

The official SDK should handle the API connection.

4. Model

Initial model:

openai/gpt-oss-20b

Groq currently documents this model in its reasoning examples.

Do not blindly assume model access. If necessary, check available
models:

models = client.models.list()
for model in models.data:
    print(model.id)

Never print credentials.

5. Minimal real connection test

Before running the autonomous research agent, perform one real Groq
request:

import os
from groq import Groq

api_key = os.environ.get("GROQ_API_KEY")

if not api_key:
    raise RuntimeError("Missing GROQ_API_KEY")

client = Groq(api_key=api_key)

response = client.chat.completions.create(
    model="openai/gpt-oss-20b",
    messages=[
        {
            "role": "user",
            "content": "Reply with exactly: GROQ_CONNECTED",
        }
    ],
)

print("GROQ_CONNECTION=SUCCESS")
print("MODEL=", response.model)
print("RESPONSE=", response.choices[0].message.content)

The response must actually come from Groq. Do not fake it.

6. OpenAI-compatible alternative

Groq also supports OpenAI-compatible clients:

import os
from openai import OpenAI

client = OpenAI(
    api_key=os.environ.get("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1",
)

response = client.chat.completions.create(
    model="openai/gpt-oss-20b",
    messages=[
        {
            "role": "user",
            "content": "Reply with exactly: GROQ_CONNECTED",
        }
    ],
)

Prefer the official groq Python SDK unless the existing architecture
already uses the OpenAI client and keeping it is materially cleaner.

Do not mix both approaches unnecessarily.

7. Research-agent architecture

The Groq provider must sit above the deterministic research engine:

ResearchAgent
    |
    +--> Read project state
    |
    +--> Read strategy/data
    |
    +--> Groq: generate hypothesis
    |
    +--> Groq: select experiment
    |
    +--> Deterministic Python experiment
    |
    +--> Actual results
    |
    +--> Groq: interpret results
    |
    +--> Groq: decision
    |
    +--> Groq: next research question
    |
    +--> Persistent state/report

The LLM must genuinely influence the research process.

Do not hard-code: - hypotheses - experiment decisions -
interpretations - next research questions

8. First autonomous demo

After the minimal connection test succeeds:

python -m app.research_agent --autonomous --max-experiments 1

For the first demo:

MAX_EXPERIMENTS=1

Exactly one research experiment must execute.

The required chain is:

REAL GROQ CALL
→ AI HYPOTHESIS
→ AI EXPERIMENT PLAN
→ REAL PYTHON EXPERIMENT
→ ACTUAL RESULTS
→ RESULTS SENT TO GROQ
→ AI INTERPRETATION
→ AI DECISION
→ NEXT RESEARCH QUESTION
→ PERSISTED REPORT
→ STOP

9. Error handling

Handle: - missing API key - invalid API key - HTTP 401 - HTTP 403 - HTTP
404 - rate limits - unavailable model - timeout - malformed response -
network/API errors

If Groq returns 403, do not assume Codespaces is incompatible.

Check: 1. GROQ_API_KEY exists. 2. The application reads
GROQ_API_KEY. 3. llmkey.md is not being used. 4. The official SDK is
being used correctly. 5. The model is available. 6. The account/key is
authorized. 7. The API endpoint is correct.

Do not run the full research experiment until the minimal Groq test
succeeds.

10. Security

If a key is ever exposed: 1. Revoke it immediately. 2. Create a
replacement. 3. Update the Codespaces secret. 4. Restart/reload the
Codespace if required.

Never put the real key in this file.

11. Trading safety

This integration is research-only.

Keep:

EXECUTION_ALLOWED=false
PAPER_ONLY=true

The LLM must never: - place Groww orders - modify orders - cancel
orders - transfer money - enable execution - bypass safety checks

Groww remains read-only.

12. Reports

Save the autonomous demo report under:

data/runs/<actual_selected_period>/reports/

Create:

ai_agent_demo_report.json
ai_agent_demo_report.md

Include: - selected period - dataset - data-quality checks - lookahead
validation - AI hypothesis - AI experiment plan - deterministic
results - AI interpretation - AI decision - next research question - LLM
provider/model - LLM call count - token usage where available - safety
status

Never store the API key.

13. Acceptance criteria

The integration is successful only when:

• GROQ_API_KEY is read from the environment
• llmkey.md is not used
• no secret is committed
• official Groq SDK or documented OpenAI-compatible method is used
• real Groq connection succeeds
• real model response is received
• AI generates a hypothesis
• AI participates in experiment planning
• deterministic research executes one experiment
• actual results are sent to Groq
• Groq interprets those results
• Groq generates the next research question
• the report is persisted
• trading execution remains disabled
• tests pass

Only then report:

GROQ_AI_AGENT=SUCCESS

Otherwise report the exact failed stage