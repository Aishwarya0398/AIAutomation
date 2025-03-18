import json
from datetime import datetime


def generate_html_report(json_file, output_file="report.html"):
    with open(json_file, "r") as f:
        data = json.load(f)

    history = data.get("history", [])

    # Start HTML report
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>Test Report</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; }
            table { border-collapse: collapse; width: 100%; }
            th, td { border: 1px solid black; padding: 8px; text-align: left; }
            th { background-color: #f2f2f2; }
            .passed { color: green; font-weight: bold; }
            .failed { color: red; font-weight: bold; }
        </style>
    </head>
    <body>
        <h1>Test Execution Report</h1>
        <p>Generated on: """ + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + """</p>
        <table>
            <tr>
                <th>Step</th>
                <th>Action</th>
                <th>Result</th>
                <th>Timestamp</th>
            </tr>
    """

    for index, entry in enumerate(history):
        step_number = entry.get("metadata", {}).get("step_number", "N/A")
        action = entry.get("model_output", {}).get("current_state", {}).get("next_goal", "N/A")
        result = entry.get("result", [{}])[0].get("extracted_content", "N/A")
        timestamp = datetime.fromtimestamp(entry.get("metadata", {}).get("step_start_time", 0)).strftime(
            "%Y-%m-%d %H:%M:%S")

        html_content += f"""
        <tr>
            <td>{step_number}</td>
            <td>{action}</td>
            <td>{result}</td>
            <td>{timestamp}</td>
        </tr>
        """

    html_content += """
        </table>
    </body>
    </html>
    """

    # Write HTML content to file
    with open(output_file, "w") as f:
        f.write(html_content)

    print(f"✅ Report generated: {output_file}")


# Run the report generation
generate_html_report("agent_results.json")
