from __future__ import annotations

from html import escape
from pathlib import Path

from .pipeline import process, sample_corrupt


def rescue_report_html(database_path: str | Path) -> str:
    result = process(sample_corrupt(), database_path)
    defects = "".join(
        "<tr>"
        f"<td>{escape(str(row['transaction_id']))}</td>"
        f"<td>{escape(str(row['rule']))}</td>"
        f"<td>{escape(str(row['severity']))}</td>"
        "</tr>"
        for row in result["defects"]
    )
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><title>Data Quality Rescue</title></head>
<body>
<h1>Data Quality Rescue</h1>
<p><strong>Run:</strong> {escape(str(result['run_id']))}</p>
<p><strong>Release status:</strong> {escape(str(result['status']))}</p>
<p>Source rows: {result['source_rows']} · Accepted: {result['accepted_rows']} · Quarantined: {result['quarantined_rows']}</p>
<h2>Defect evidence</h2>
<table><thead><tr><th>Transaction</th><th>Rule</th><th>Severity</th></tr></thead><tbody>{defects}</tbody></table>
<p><small>Synthetic data-quality incident.</small></p>
</body></html>"""


def write_rescue_report(database_path: str | Path, output_path: str | Path) -> Path:
    html = rescue_report_html(database_path)
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(html, encoding="utf-8")
    return output
