# Ticket Email Report

This project is a Streamlit-based app that reads ticket data from an Excel or CSV file and generates a professional daily email report for support teams. It groups tickets by assignment group, summarizes their status, and creates an HTML email preview that can be downloaded as an `.eml` or `.html` file.

## What the app does

- Uploads a ticket file in `.csv`, `.xlsx`, or `.xls` format
- Maps each ticket to a team such as Sales, CDA, ECS, MarTech, or Digital
- Counts tickets by state/status
- Builds a daily summary table for the report
- Creates a formatted HTML email body with ticket details
- Lets you download the report as an Outlook-style `.eml` draft or as raw HTML

## Required input columns

Your uploaded spreadsheet must include these columns:

- `Assignment group`
- `State`

The app reads these to classify and summarize the ticket data.

## Example workflow

1. Open the app in your browser.
2. Upload the ticket export file.
3. Enter the daily summary values:
   - Date
   - Day opening count number
   - Number of tickets opened for the day
   - Tickets resolved during the day
   - Resource name
   - Shift
4. Preview the generated email.
5. Download the report as `.eml` or `.html`.

## Tech stack

- Python
- Streamlit
- Pandas
- EmailMessage (standard Python library)

## Prerequisites

Install Python 3.9 or later and then install the required packages:

```bash
pip install streamlit pandas
```

## Run the app

From the project folder, run:

```bash
streamlit run app.py
```

The app will open in your browser and you can start uploading files.

## Project structure

```text
Ticket_count_mail/
├── app.py
├── README.md
└── your_ticket_file.csv or .xlsx
```

## Notes

- The app is designed for daily support team ticket reporting.
- The output is aimed at internal operational summaries rather than a general-purpose ticket system.
- The `Assignment group` names should match the expected team categories used in the app, or they may be listed as unmatched in the UI.

## License

This project is for internal or personal use unless a separate license is provided.
