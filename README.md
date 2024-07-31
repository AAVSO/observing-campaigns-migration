# observing-campaigns-migration

## Overview

The American Association of Variable Star Observers regularly gets requests from researchers for
data collection on stars or novae. Since the 1990s, we've conducted over 600 campaigns, all of
which required migration to a new application. By using the Chat-GPT API, I saved our staff weeks
of time. The API extracted key information from text documents such as “abstract”, “targets”, and
“principal investigator” converting them to JSON format in order to populate our database.



![migration_demo](https://github.com/user-attachments/assets/d242c215-2952-48d5-af10-1315ec22eab5)


## Migration

A Python scraper fetched HTML pages from observing campaigns
and converted them into markdown to minimize noise. The data was
then processed into JSON format, marking uncertain fields as N/A,
and sent to the Chat-GPT OpenAI API. To save time, this process
was done in parallel, allowing over 600 campaigns to be converted
within 3 hours. The resulting data was transferred to a CSV for
review and cross-referenced with the VSX star database for linking
star information, before being added to the application database.

## Usage

Run `pipenv run migration [start] [end] [out_file]`

where `start` and `end` are alert notice ids and `out_file` is where to output data.
