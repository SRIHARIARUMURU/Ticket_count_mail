from datetime import date
from email.message import EmailMessage
from html import escape

import pandas as pd
import streamlit as st

GREETING = "Hi Aslam,"
TABLE_HEADERS = ["Date", "Day opening count number", "Number of tickets opened for the day",
                 "Tickets Resolved during the day", "Closing tickets count"]

# Assessment groups per team
TEAMS = {
    "CDA": [
        "BI-IIM", "Client Data and Analytics Application Support", "EIM GDS International Support",
        "EIM GDS USAS Team", "GID - Third Party Processing Applications", "GAS digital engagement support",
        "INDIA SALES REPORTING Services", "India Sales & Reporting AD Support", "MOM Support Group",
        "Competitive Intelligence (CI) Support & Approval", "LM - TAOS Support", "LM-TAOS Support",
    ],
    "ECS": ["Enterprise Client Systems"],
    "MarTech": [
        "Global Marketing Systems - Digital Marketing Support Tools", "Global Marketing Systems - Operations Support",
        "Global Marketing Systems - Reporting Tools", "Widen Application Support",
        "Commercial Print / Marketing Operations", "Global Information Portal Support and Approval",
        "TIMES Support", "Global Marketing Systems - Operations Approval",
        "Event Management AD Support Approval", "GRIP (Global Reporting and Information Platform)",
        "Extream application", "GRIP Application Support",
    ],
    "Sales": [
        "Dynamics CRM", "Global Sales Compensation Support", "India Sales CRM Application Support",
        "Fund Analysis Tool Application Support",
    ],
    "Digital": ["Global Web Technology Group"],
}
GROUP_TO_TEAM = {g.lower(): t for t, groups in TEAMS.items() for g in groups}

# Status label -> keyword searched (case-insensitive) in the status column
STATUS_KEYWORDS = {
    "Active": "active", "Awaiting Vendor": "vendor", "On Hold Monitoring": "hold",
    "Awaiting Customer": "customer", "Awaiting release": "release", "Workaround in Place": "workaround",
}
# Teams listed in the detail bullets, with the statuses shown for each
BULLET_TEAMS = {
    "Sales": ["Active", "Awaiting Vendor", "On Hold Monitoring", "Workaround in Place"],
    "ECS": ["Active", "On Hold Monitoring", "Awaiting Customer"],
    "CDA": ["Active", "On Hold Monitoring", "Awaiting Customer", "Awaiting Vendor", "Workaround in Place"],
    "MarTech": ["Active", "Awaiting Customer", "Awaiting release", "Awaiting Vendor", "On Hold Monitoring"],
}


def n2(n):
    return f"{n:02d}"


def count_status(status, keywords):
    return int(status.str.contains("|".join(keywords), regex=True).sum())


def build_email(rep_date, opening, opened, resolved, df, group_col, status_col, resource):
    team = df[group_col].astype(str).str.strip().str.lower().map(GROUP_TO_TEAM)
    status = df[status_col].astype(str).str.lower()
    closing = len(df)
    total = team.value_counts()

    def tickets(name):
        return int(total.get(name, 0))

    def detail(name, statuses):
        mask = team == name
        parts = [f"{n2(count_status(status[mask], [STATUS_KEYWORDS[s]]))} {s}" for s in statuses]
        return f"{name} {n2(tickets(name))} {'ticket' if tickets(name) == 1 else 'tickets'} ({', '.join(parts)})."

    handled = sum(tickets(t) for t in BULLET_TEAMS)
    digital_active = int(((team == "Digital") & (status.str.strip() == "active")).sum())
    digital_other = tickets("Digital") - digital_active
    cell = "border:1px solid #999;padding:6px 10px;text-align:center;"
    head = "".join(f'<td style="{cell}">{h}</td>' for h in TABLE_HEADERS)
    row = "".join(f'<td style="{cell}">{v}</td>' for v in
                  [rep_date.strftime("%d/%m/%Y"), opening, n2(opened), n2(resolved), closing])
    working = "(Team is working on it)."
    summary = [("Digital Web Track", "Digital"), ("MarTech track", "MarTech"), ("Sales", "Sales"),
               ("ECS", "ECS"), ("CDA", "CDA")]
    summary_html = "<br>".join(f"{label} – {n2(tickets(t))} tickets {working}" for label, t in summary)
    bullets = "".join(f"<li>{detail(t, s)}</li>" for t, s in BULLET_TEAMS.items())
    p = '<p style="margin:0 0 18px 0;">'

    html = f"""<div style="font-family:Calibri,Arial,sans-serif;font-size:14px;">
{p}{GREETING}</p>
{p}PFB ticket details :</p>
<table style="border-collapse:collapse;margin-bottom:18px;"><tr>{head}</tr><tr>{row}</tr></table>
{p}{summary_html}</p>
{p}{n2(digital_active)} tickets are waiting for the requestor confirmation once we get confirmation ticket will be closed.</p>
{p}{n2(digital_other)} tickets are waiting for code fix and release. (Jira is in place and discussion is going on for ETA of release).</p>
{p}{n2(handled)} tickets are being handling by Sales, CDA, ECS and MarTech team, below are the details.</p>
<ul>{bullets}</ul>
<p><b>Regards,<br>{escape(resource)}.</b></p>
</div>"""
    return html, team


st.set_page_config(page_title="Ticket Email Report", layout="wide")
st.title("Ticket Email Report")

file = st.file_uploader("Upload Excel or CSV", type=["xlsx", "xls", "csv"])
if file is None:
    st.stop()

df = (pd.read_csv(file, encoding_errors="replace") if file.name.lower().endswith(".csv")
      else pd.read_excel(file))
df.columns = [str(c).strip() for c in df.columns]


group_col = "Assignment group"
status_col = "State"
missing_columns = [column for column in (group_col, status_col) if column not in df.columns]
if missing_columns:
    st.error(f"Missing required columns: {', '.join(missing_columns)}")
    st.stop()

c1, c2, c3, c4, c5 = st.columns(5)
rep_date = c1.date_input("Date", date.today(), format="DD/MM/YYYY")
opening = c2.number_input("Day opening count number", min_value=0, step=1)
opened = c3.number_input("Number of tickets opened for the day", min_value=0, step=1)
resolved = c4.number_input("Tickets Resolved during the day", min_value=0, step=1)
resource = c5.text_input("Resource Name", "Srihari Arumuru")
shift = st.radio("Shift", ["Morning", "Afternoon", "Night"], horizontal=True)

html, team = build_email(rep_date, int(opening), int(opened), int(resolved), df, group_col, status_col, resource)

st.metric("Closing tickets count", len(df))
if team.isna().any():
    missing = df.loc[team.isna(), group_col].astype(str).str.strip().unique()
    st.warning(f"{team.isna().sum()} tickets not matched to any team: {', '.join(missing)}")

st.subheader("Email preview")
with st.container(border=True):
    st.html(html)

msg = EmailMessage()
msg["Subject"] = f"Daily Report on the GAS Tickets Status of {rep_date.strftime('%d/%m/%Y')} -  {shift} Shift"
msg["X-Unsent"] = "1"
msg.set_content("Please view this email in HTML.")
msg.add_alternative(html, subtype="html")

d1, d2 = st.columns(2)
d1.download_button("Download .eml (opens as Outlook draft)", bytes(msg), "ticket_report.eml", "message/rfc822")
d2.download_button("Download .html", html, "ticket_report.html", "text/html")
