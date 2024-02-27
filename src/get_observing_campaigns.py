"""
get_observing_campaigns.py

Fetches the content of an AAVSO Alert Notice and extracts specific information into a JSON object.

Fields Extracted:
    - Title
    - Principal Investigator
    - Abstract
    - Justification
    - Target Object
    - Start Date
    - End Date
    - Status

Usage: pipenv run python get_alert_notices.py
"""

import json
import os

import fire
import html2text
import requests
from bs4 import BeautifulSoup
from openai import OpenAI


def fetch_alert_notice(notice_id):
    """Retrieve the content of the given AAVSO Alert Notice."""
    alert_notice_url = f"https://www.aavso.org/aavso-alert-notice-{notice_id}"
    response = requests.get(alert_notice_url)
    soup = BeautifulSoup(response.content, 'html.parser').find('div', class_='main-container')
    html_as_text = html2text.HTML2Text().handle(str(soup))
    main_content = html_as_text[:-1200]
    return main_content


def extract_information_from_page(openai_client, model, content, output_format):
    """Use OpenAI to extract the desired fields from the AAVSO Alert Notice content."""
    query = (
        "The following is an Observing Campaign published by the AAVSO. Extract the following information into a json object "
        "Title, Principal Investigator, Abstract, Justification, Target Object, Start Date, End Date, and Status. "
        "Unknown fields should be marked as N/A. Dates should be in the 'YYYY-MM-DD' format."
    )

    chat_completion = openai_client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": f"{query}\n\n{content}"}],
        tools=[{"type": "function", "function": output_format}]
    )

    output = chat_completion.choices[0].message.tool_calls[0].function.arguments
    return json.loads(output)


async def process_alert_notices(start, end, out_file):
    client = OpenAI()
    model = os.environ.get("OPENAI_MODEL")
    with open("src/output_format.json") as f:
        output_format = json.load(f)

    alert_notices = range(start, end)

    data = {}

    for alert_notice_id in alert_notices:
        print(f"Fetching content for alert notice {alert_notice_id}...")
        content = fetch_alert_notice(alert_notice_id)

        print("Extracting information...")
        output = extract_information_from_page(client, model, content, output_format)

        data[alert_notice_id] = output

        # Save data to file
        with open(out_file, "w+") as f:
            json.dump(data, f)

    print(f"Data extraction completed and saved to {out_file}")


if __name__ == '__main__':
    fire.Fire(process_alert_notices)
