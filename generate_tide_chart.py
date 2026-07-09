import os
import numpy as np
from datetime import datetime, date, timedelta
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

def generate_dashboard():
    filepath = "Hampton Tides.txt"
    if not os.path.exists(filepath):
        print(f"Error: {filepath} not found.")
        return

    # Target today's date
    current_day = date.today()
    
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

            # Collect data matching today's window
            if dt.date() == current_day:
                times.append(dt)
                heights.append(height_val)
                
                # Capture the explicit markers in your file
                if "HIGHTIDE" in state:
                    high_tides.append((dt, height_val))
                elif "LOWTIDE" in state:
                    low_tides.append((dt, height_val))

    if not times:
        print(f"No data found for today ({current_day}).")
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
        plt.annotate(f"{h:.2f}m\n{time_str}", (dt, h), 
                     textcoords="offset points", xytext=(0, -25), 
                     ha='center', va='top', weight='bold', color='#1b5e20',
                     bbox=dict(boxstyle="round,pad=0.2", fc="white", ec="#a5d6a7", alpha=0.8, zorder=4))
                     
    # Highlight Low points (Labels cleanly flipped ABOVE the dot)
    for dt, h in low_tides:
        plt.scatter(dt, h, color='#c62828', s=50, zorder=5)
        time_str = dt.strftime('%I:%M %p').lstrip('0')
        plt.annotate(f"{h:.2f}m\n{time_str}", (dt, h), 
                     textcoords="offset points", xytext=(0, 15), 
                     ha='center', va='bottom', weight='bold', color='#b71c1c',
                     bbox=dict(boxstyle="round,pad=0.2", fc="white", ec="#ef9a9a", alpha=0.8, zorder=4))

    # Formatting axes cleanly
    plt.title(f"Westfield Tidal Predictions — {current_day.strftime('%A, %B %d')}", fontsize=14, pad=15, weight='bold')
    plt.ylabel("Water Height (m)")
    
    # Dynamic Y-Axis Limits with 0.1m Buffer
    y_min = min(heights) - 0.1
    y_max = max(heights) + 0.1
    plt.ylim(y_min, y_max)
    
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

    # Build the final index page with the text headers removed completely
    html_content = f"""<!DOCTYPE html>
<html>
<head>
    <title>Hampton Tide Dashboard</title>
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
            padding: 3px;
            border-radius: 12px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        }}
        img {{ max-width: 100%; height: auto; border-radius: 6px; border: 1px solid #ddd; display: block; margin: 0 auto; }}
    </style>
</head>
<body>
    <div class="container">
        <img src="{graph_path}" alt="Today's Tide Curve">
    </div>
</body>
</html>
"""
    with open("index.html", "w") as f:
        f.write(html_content)
    print("Dashboard updated: HTML headers removed successfully!")

if __name__ == "__main__":
    generate_dashboard()
