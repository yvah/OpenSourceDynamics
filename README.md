# SwEng-group13

## Analytics Solution on OpenSource Dev Community Dynamics

Understanding, and interacting with, the Open-Source
community is, nowadays, a vital part of the Software Engineering
profession. This project is proposing to create a sophisticated AI
Application capable to ingest large amount of activity logs,
publicly available, from the various Open-Source portals and use
Natural Language Understanding and Analytics tools/techniques
provide aggregated insights on trends, dynamics and facts
behind the Community.

## API Release

In order to run NL analysis, add IBM Watson NLU API key & url into `keys.txt`.
Enter a GitHub Access Token and enter the name and owner of the repo you want to gather data from.
Finally, specify whether you want to get issue or pull requests.
If the comments are already in the database, you will be asked whether you want to use the existing data.

JSON files with extracted information will be stored in `cwd/fetched_data` folder.
To run API Queries independently from NL processing, open `query.py` and run the main function.
