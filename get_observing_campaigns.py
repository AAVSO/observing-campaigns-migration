"""
get_alert_notices.py

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

Usage: python get_alert_notices.py
"""

import os
import json
import requests
import openai
from bs4 import BeautifulSoup
import html2text


def fetch_alert_notice(notice_id):
    """Retrieve the content of the given AAVSO Alert Notice."""
    alert_notice_url = f"https://www.aavso.org/aavso-alert-notice-{notice_id}"
    response = requests.get(alert_notice_url)
    soup = BeautifulSoup(response.content, 'html.parser').find('div', class_='main-container')
    return html2text.HTML2Text().handle(str(soup))[:-1200]


def extract_information_from_page(content, api_key, model="gpt-4"):
    """Use OpenAI to extract the desired fields from the AAVSO Alert Notice content."""
    openai.api_key = api_key
    query = (
        "The following is an Observing Campaign published by the AAVSO. Extract the following information into a json object "
        "Title, Principal Investigator, Abstract, Justification, Target Object, Start Date, End Date, and Status. "
        "Unknown fields should be marked as N/A. Dates should be in the 'YYYY-MM-DD' format. "
        "Status should be either 'Active' or `Concluded`. Use the canonical VSX name for the target object "
        "and separate multiple objects with a semicolon. All fields should be strings. Return only the json object."
    )

    chat_completion = openai.ChatCompletion.create(
        model=model, messages=[{"role": "user", "content": f"{query}\n\n{content}"}])

    return chat_completion['choices'][0]['message']["content"]


def main():
    """Main function to orchestrate the extraction process."""
    data = {}
    openai_api_key = os.environ.get("OPENAI_API_KEY")
    alert_notices = range(548, 600)

    for alert_notice_id in alert_notices:
        print(f"Fetching content for alert notice {alert_notice_id}...")
        content = fetch_alert_notice(alert_notice_id)

        print("Extracting information...")
        output = extract_information_from_page(content, openai_api_key)

        try:
            data[alert_notice_id] = json.loads(output)
            print(data[alert_notice_id])
        except json.JSONDecodeError:
            print(f"Failed to parse output: {output}")

    # Save data to file
    with open("data.json", "w+") as f:
        json.dump(data, f)

    print("Data extraction completed and saved to data.json.")


if __name__ == '__main__':
    main()
