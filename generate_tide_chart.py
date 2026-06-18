import os
import numpy as np
from datetime import datetime, date, timedelta
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

def generate_dashboard():
    filepath = "Westfield Tides.txt"
    if not os.path.exists(filepath):
        print(f"Error: {filepath} not found.")
        return

    # Target tomorrow's date
    tomorrow = date.today() + timedelta(days=1)
    
    times = []
    heights = []
    high_tides = []
    low_tides = []

    # Read and parse your dataset
    with open(filepath, "r") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            
            # Split by tabs
            parts = line.split("\t")
            if len(parts) < 3:
                continue
                
            datetime_str = parts[0].strip()   # e.g., "2026-06-19 5:46"
            height_val = float(parts[1].strip()) # e.g., 0.715381171
            state = parts[2].strip()          # e.g., "HIGHTIDE" or "FALLING"
            
            try:
                dt = datetime.strptime(datetime_str, "%Y-%m-%d %H:%M")
            except ValueError:
                continue

            # Only collect data matching tomorrow's full window
            if dt.date() == tomorrow:
                times.append(dt)
                heights.append(height_val)
                
                # Capture the explicit markers in your file
                if "HIGHTIDE" in state:
                    high_tides.append((dt, height_val))
                elif "LOWTIDE" in state:
                    low_tides.append((dt, height_val))

    if not times:
        print(f"No data found for tomorrow ({tomorrow}).")
        return

    # --- Generate the Graph Curve ---
    plt.figure(figsize=(9, 4.5))
    
    # Plot the raw path points smoothly
    plt.plot(times, heights, color='#1565c0', linewidth=2.5, label='Water Level')
    plt.fill_between(times, heights, color='#e3f2fd', alpha=0.5)
    
    # Highlight High points (Labels STACKED BELOW the dot)
    for dt, h in high_tides:
        plt.scatter(dt, h, color='#2e7d32', s=50, zorder=5)
        time_str = dt.strftime('%I:%M %p').lstrip('0')
        # xytext=(0, -25) moves the text block down below the high peak marker
        plt.annotate(f"{h:.2f}m\n{time_str}", (dt, h), 
                     textcoords="offset points", xytext=(0, -25), 
                     ha='center', va='top', weight='bold', color='#1b5e20',
                     bbox=dict(boxstyle="round,pad=0.2", fc="white", ec="#a5d6a7", alpha=0.8, zorder=4))
                     
    # Highlight Low points (Labels cleanly placed below or offset depending on y-axis floor)
    for dt, h in low_tides:
        plt.scatter(dt, h, color='#c62828', s=50, zorder=5)
        time_str = dt.strftime('%I:%M %p').lstrip('0')
        # Placed slightly below the low points
        plt.annotate(f"{h:.2f}m\n{time_str}", (dt, h), 
                     textcoords="offset points", xytext=(0, -25), 
                     ha='center', va='top', weight='bold', color='#b71c1c',
                     bbox=dict(boxstyle="round,pad=0.2", fc="white", ec="#ef9a9a", alpha=0.8, zorder=4))

    # Formatting axes cleanly
    plt.title(f"Westfield Tidal Predictions — {tomorrow.strftime('%A, %B %d, %Y')}", fontsize=14, pad=15, weight='bold')
    plt.ylabel("Water Height (m)")
    
    # TWEAK: Start the Y-axis exactly at 0.2 meters
    plt.ylim(bottom=0.2)
    
    ax = plt.gca()
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%I:%M %p'))
    ax.xaxis.set_major_locator(mdates.HourLocator(interval=3)) # Clean tick every 3 hours
    plt.xticks(rotation=15)
    plt.grid(True, linestyle='--', alpha=0.3)
    plt.tight_layout()
    
    # Save chart asset
    os.makedirs("assets", exist_ok=True)
    graph_path = "assets/tide_chart.png"
    plt.savefig(graph_path, dpi=150)
    plt.close()

    # --- Construct the HTML Strings ---
    high_html = "".join([f"<li><strong>{dt.strftime('%I:%M %p').lstrip('0')}:</strong> {h:.2f}m</li>" for dt, h in high_tides])
    low_html = "".join([f"<li><strong>{dt.strftime('%I:%M %p').lstrip('0')}:</strong> {h:.2f}m</li>" for dt, h in low_tides])

    # Build the final index page
    html_content = f"""<!DOCTYPE html>
<html>
<head>
    <title>Westfield Tide Dashboard</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            padding: 20px 10px;
            background-color: #f4f6f9;
            color: #333;
            text-align: center;
        }}
        .container {{
            max-width: 800px;
            margin: 0 auto;
            background: #ffffff;
            padding: 25px;
            border-radius: 12px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        }}
        h1 {{ font-size: 1.5rem; color: #111; margin-bottom: 5px; }}
        .date-sub {{ font-size: 1.1rem; color: #666; margin-bottom: 25px; }}
        .tide-lists {{
            display: flex;
            justify-content: space-around;
            text-align: left;
            margin: 20px 0;
            gap: 15px;
        }}
        .box {{
            flex: 1;
            padding: 15px;
            border-radius: 8px;
            background: #fafafa;
            border: 1px solid #eee;
        }}
        ul {{ list-style: none; padding: 0; margin: 0; }}
        li {{ margin: 10px 0; font-size: 1.1rem; }}
        .high-title {{ color: #2e7d32; border-bottom: 2px solid #a5d6a7; padding-bottom: 5px; margin-top: 0; }}
        .low-title {{ color: #c62828; border-bottom: 2px solid #ef9a9a; padding-bottom: 5px; margin-top: 0; }}
        img {{ max-width: 100%; height: auto; margin-top: 20px; border-radius: 6px; border: 1px solid #ddd; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Westfield Tide Station</h1>
        <div class="date-sub">{tomorrow.strftime('%A, %B %d, %Y')}</div>
        
        <div class="tide-lists">
            <div class="box">
                <h3 class="high-title">▲ High Tides</h3>
                <ul>{high_html or "<li>No high tides tomorrow</li>"}</ul>
            </div>
            <div class="box">
                <h3 class="low-title">▼ Low Tides</h3>
                <ul>{low_html or "<li>No low tides tomorrow</li>"}</ul>
            </div>
        </div>

        <img src="{graph_path}" alt="Tomorrow's Tide Curve">
    </div>
</body>
</html>
"""
    with open("index.html", "w") as f:
        f.write(html_content)
    print("Dashboard and chart built successfully with new layout tweaks!")

if __name__ == "__main__":
    generate_dashboard()
