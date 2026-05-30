"""
Example: call the Google Patents API Apify Actor from Python.

Search Google Patents by keyword, inventor, or assignee and get clean,
structured JSON: title, snippet, inventors, assignees, dates, publication
number, and a PDF link per patent. An AI summary block (top assignees,
inventors, and CPC classes with year-range frequencies) is attached to the
first page item. Set include_details to also pull claims, citations, and
family members for each result; set patent_id to fetch one patent directly.

This example runs one search page to keep the first run inexpensive (each page
is one billed event). Raise max_pages for deeper coverage.

Get your free Apify API key at: https://apify.com?fpr=9n7kx3
Set it in a .env file (see .env.example) or export APIFY_API_TOKEN.
"""

import os

from apify_client import ApifyClient
from dotenv import load_dotenv

load_dotenv()

APIFY_API_TOKEN = os.getenv("APIFY_API_TOKEN")
if not APIFY_API_TOKEN:
    raise SystemExit(
        "APIFY_API_TOKEN is not set. Copy .env.example to .env and add your key, "
        "or run: export APIFY_API_TOKEN=your_api_key_here"
    )

client = ApifyClient(APIFY_API_TOKEN)

run_input = {
    "q": "semiconductor cooling",
    "num": 10,
    "max_pages": 1,
    # "assignee": "Apple,Microsoft",   # filter by company
    # "inventor": "Jane Doe",          # filter by inventor
    # "patent_id": "patent/US11734097B1/en",  # details mode for a single patent
}

print(f"Searching Google Patents for: {run_input['q']}")
run = client.actor("johnvc/google-patents-api").call(run_input=run_input)
if run is None:
    raise SystemExit("The Actor run did not start. Check your API token and inputs.")

for page in client.dataset(run.default_dataset_id).iterate_items():
    metadata = page.get("search_metadata", {})
    patents = page.get("patents", [])
    print(
        f"\nPage {page.get('page_number', '?')}: {len(patents)} patents "
        f"(total matching: {metadata.get('total_results', 'n/a')})\n"
    )

    for pt in patents:
        assignees = ", ".join(pt.get("assignee") or []) or "n/a"
        inventors = ", ".join(pt.get("inventor") or []) or "n/a"
        date = pt.get("grant_date") or pt.get("publication_date") or pt.get("priority_date") or ""
        print(f"  {pt.get('position')}. {pt.get('title')}")
        print(f"     {pt.get('publication_number')}  |  {date}")
        print(f"     Assignee: {assignees}")
        print(f"     Inventor: {inventors}")
        print(f"     PDF: {pt.get('pdf')}")
        print()

    ai = page.get("ai_summary")
    if ai:
        print(
            f"AI summary attached: {len(ai.get('assignees') or [])} assignee buckets, "
            f"{len(ai.get('inventors') or [])} inventor buckets, "
            f"{len(ai.get('cpc') or [])} CPC-class buckets."
        )
