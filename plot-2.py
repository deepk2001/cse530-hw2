import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import re
import os
from scipy.interpolate import make_interp_spline


data_file = "experiment_2_saved_data.txt"


output_folder = "plots_experiment_2"
os.makedirs(output_folder, exist_ok=True)


with open(data_file, "r") as f:
    lines = f.readlines()


def parse_line(line):
    parts = [x.strip() for x in line.split(",") if x.strip()]
    key = parts[0]
    values = [float(x) for x in parts[1:] if re.match(r"^-?\d+(\.\d+)?$", x)]
    return key, values


data_dict = {}
for line in lines:
    if not line.strip():
        continue
    key, values = parse_line(line)
    data_dict[key] = values

# Ensure associativity exists
if "associativity" not in data_dict:
    raise ValueError("Missing 'associativity' entry in the data file.")

associativitys = np.array(data_dict["associativity"])


for metric, values in data_dict.items():
    if metric == "associativity":
        continue

    y = np.array(values)

    if len(y) != len(associativitys):
        print(f"⚠️ Skipping {metric}: length mismatch ({len(y)} vs {len(associativitys)})")
        continue


    X_smooth = np.linspace(associativitys.min(), associativitys.max(), 500)
    spline = make_interp_spline(associativitys, y, k=3)
    Y_smooth = spline(X_smooth)

    plt.figure(figsize=(8, 5))
    plt.plot(X_smooth, Y_smooth, color='blue', linewidth=2)
    plt.scatter(associativitys, y, color='red', s=10, label="data points")
    plt.xlabel("Associativity")
    plt.ylabel(metric)
    plt.title(f"{metric} vs Associativity")
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.legend()
    plt.tight_layout()


    safe_name = re.sub(r"[^a-zA-Z0-9_]+", "_", metric)
    plt.savefig(os.path.join(output_folder, f"{safe_name}.png"), dpi=300)
    plt.close()

print(f"✅ Smooth continuous curve plots saved in folder: '{output_folder}'")