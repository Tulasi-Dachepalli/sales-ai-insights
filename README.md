# AI-Powered Sales Insights Assistant

An interactive analytics dashboard that lets a user ask plain-English
questions about sales data ("Which region underperformed last quarter
and why?") and get an AI-generated, data-grounded answer — alongside a
standard Power BI-style dashboard (region, category, and monthly trend
views).

Built to demonstrate: data cleaning, exploratory analysis, dashboarding,
and integrating an LLM as an analysis layer on top of real business data.

---

## Project structure

```
sales_ai_project/
├── generate_data.py       # Creates a realistic synthetic sales dataset
├── clean_and_analyze.py   # Cleans data + prints key business insights
├── app.py                 # Streamlit dashboard + AI query interface
├── requirements.txt
├── data/
│   ├── sales_data.csv     # Raw generated data (with intentional messiness)
│   └── sales_clean.csv    # Cleaned data (created after running clean_and_analyze.py)
└── README.md
```

## What each script demonstrates

| File | Skill shown |
|---|---|
| `generate_data.py` | Understanding of realistic business data patterns (seasonality, regional bias, margin differences) |
| `clean_and_analyze.py` | Data cleaning judgment (standardizing text, handling nulls with a documented assumption, sanity-check assertions), groupby analysis |
| `app.py` | Dashboarding (Plotly/Streamlit), and grounding an LLM's answers in real aggregated data instead of letting it hallucinate |

---

## How to run it locally

**1. Install dependencies**
```bash
pip install -r requirements.txt
```

**2. Generate and clean the data**
```bash
python generate_data.py
python clean_and_analyze.py
```

**3. Get a free Anthropic API key**
- Go to https://console.anthropic.com
- Sign up, create an API key
- Set it as an environment variable:
  ```bash
  # Mac/Linux
  export ANTHROPIC_API_KEY="your-key-here"

  # Windows (Command Prompt)
  setx ANTHROPIC_API_KEY "your-key-here"
  ```

**4. Run the app**
```bash
streamlit run app.py
```
This opens the dashboard in your browser at `http://localhost:8501`.

---

## Deploying it live (so you can share a real link)

1. Push this folder to a public GitHub repo.
2. Go to https://share.streamlit.io (Streamlit Community Cloud — free).
3. Connect your GitHub repo, point it at `app.py`.
4. Add your `ANTHROPIC_API_KEY` under the app's "Secrets" settings (never commit it to GitHub directly).
5. Deploy. You'll get a public URL like `https://yourname-sales-ai.streamlit.app`.

Put that link on your resume, LinkedIn Featured section, and in your GitHub profile.

---

## How to talk about this in an interview

**30-second pitch:**
> "I built an AI-powered sales dashboard that lets a non-technical user ask
> plain-English questions about the data instead of digging through filters.
> I generated a realistic sales dataset, cleaned it with documented
> assumptions, built the standard trend/region/category views, then added
> an LLM layer that answers questions grounded strictly in the aggregated
> numbers — so it never makes up figures. It's deployed live on Streamlit
> Cloud."

**If asked "how do you stop the AI from hallucinating numbers":**
> "I don't let the model see the raw dataset. I pre-compute the summary
> tables with Pandas and only pass those aggregates into the prompt, so
> the model can only reason over real numbers I've already verified."

**If asked "what would you improve":**
> "Add caching for repeated questions, expand the AI to trigger specific
> chart generation based on the question, and swap the synthetic dataset
> for a real one via a data warehouse connection."

---

## Resume / LinkedIn bullet

> Built and deployed an AI-powered sales analytics assistant enabling
> natural-language querying over business data (Python, Pandas, Streamlit,
> Anthropic API), reducing manual reporting effort by surfacing
> region/category insights instantly — live demo available.

---

## Notes on the dataset

The dataset is synthetically generated with realistic business patterns
(holiday seasonality, a weaker Central region, thinner Electronics
margins) — this is intentional so the AI and dashboard have genuine,
explainable insights to surface, and so you can confidently explain
*why* each number looks the way it does in an interview. It also
includes deliberately introduced messiness (missing discounts,
inconsistent casing, stray whitespace) so the cleaning script has real
problems to solve, not just placeholder code.
