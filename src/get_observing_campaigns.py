"""
get_observing_campaigns.py

Fetches the content of AAVSO Alert Notices asynchronously and extracts specific information into a JSON object.

Usage: pipenv run python get_alert_notices.py
"""

import asyncio
import json
import os

import aiohttp
import fire
import html2text
from bs4 import BeautifulSoup
from openai import AsyncOpenAI
from tenacity import retry, wait_fixed, stop_after_attempt


async def fetch_alert_notice(session, notice_id):
    """Retrieve the content of the given AAVSO Alert Notice asynchronously."""

    # cache pages
    try:
        with open(f'data/pages/{notice_id}.txt', 'r') as f:
            return f.read()
    except FileNotFoundError:
        pass

    alert_notice_url = f"https://www.aavso.org/aavso-alert-notice-{notice_id}"

    async with session.get(alert_notice_url) as response:
        content = await response.text()
        soup = BeautifulSoup(content, 'html.parser').find('div', class_='main-container')
        html_as_text = html2text.HTML2Text().handle(str(soup))
        main_content = html_as_text[:-1200]
        with open(f'data/pages/{notice_id}.txt', 'w') as f:
            f.write(main_content)
        return main_content


@retry(stop=stop_after_attempt(3), wait=wait_fixed(5))
async def extract_information_from_page(openai_client, model, content, output_format):
    """Use OpenAI to extract the desired fields from the AAVSO Alert Notice content asynchronously."""

    query = (
        "The following is an Observing Campaign published by the AAVSO. Extract the following information into a json object "
        "Title, Principal Investigator, Abstract, Justification, Target Object, Spectral Lines, Filters, Start Date, End Date, and Status. "
        "Unknown fields should be marked as N/A (or false for booleans). "
    )

    chat_completion = await openai_client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": f"{query}\n\n{content}"}],
        tools=[{"type": "function", "function": output_format}]
    )

    output = chat_completion.choices[0].message.tool_calls[0].function.arguments
    return json.loads(output)


async def process_alert_notice(session, openai_client, model, output_format, alert_notice_id):
    print(f"Fetching content for alert notice {alert_notice_id}...")
    content = await fetch_alert_notice(session, alert_notice_id)

    if len(content) == 0:
        return alert_notice_id, {}

    print(f"Extracting information for alert notice {alert_notice_id}...")
    try:
        output = await extract_information_from_page(openai_client, model, content, output_format)
    except Exception as e:
        print(e)
        return alert_notice_id, {"error": "Failed to extract information"}

    return alert_notice_id, output


async def process_alert_notices(start, end, out_file):
    client = AsyncOpenAI()
    model = os.environ.get("OPENAI_MODEL")
    with open("src/output_format.json") as f:
        output_format = json.load(f)

    alert_notices = range(start, end)

    with open(out_file, "r") as f:
        json_data = json.load(f)
        alert_notices = [notice_id for notice_id in alert_notices if 'error' in json_data[str(notice_id)]]

    print(alert_notices)
    data = json_data

    async with aiohttp.ClientSession() as session:
        tasks = [process_alert_notice(session, client, model, output_format, alert_notice_id)
                 for alert_notice_id in alert_notices]
        results = await asyncio.gather(*tasks)

        for alert_notice_id, output in results:
            data[alert_notice_id] = output

            # Save data to file after each completed task
            with open(out_file, "w+") as f:
                json.dump(data, f)

    print(f"Data extraction completed and saved to {out_file}")


def main(start, end, out_file):
    asyncio.run(process_alert_notices(start, end, out_file))


if __name__ == '__main__':
    fire.Fire(main)
