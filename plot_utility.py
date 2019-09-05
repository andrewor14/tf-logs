#!/usr/bin/env python

import os
import sys

import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import numpy as np

import parse


def plot(log_dirs):
  # func_args => list of (price, total time)
  linear_function_data = {}
  step_function_data = {}
  all_prices = []
  for log_dir in log_dirs:
    experiment_name = log_dir.split("/")[-1]
    func_name, func_args, price, _ = experiment_name.split("-")
    price = float(price)
    # Parse total time from logs
    total_time = None
    print("Parsing total time from %s" % log_dir)
    parsed = parse.parse_dir(log_dir, "total_time")[1]
    if len(parsed) == 1:
      total_time = float(parsed[0])
    # We may have used "_" instead of ":" so bash parses the variable
    # names correctly, so here we substitute it back
    if func_name == "step":
      func_args = func_args.replace("_", ":")
    # Save parsed time to the right map
    data_map = linear_function_data if func_name == "linear" else step_function_data
    if func_args not in data_map:
      data_map[func_args] = []
    if total_time is not None:
      data_map[func_args].append((price, total_time))
    else:
      print("Warning: total time was not available for %s" % experiment_name)
    if price not in all_prices:
      all_prices.append(price)
  # Decide how many plots to make
  # We align all the linear and step plots
  out_file = "output/utility.pdf"
  fig, axes = plt.subplots(nrows=len(linear_function_data), ncols=2)
  color_cycle = ["r", "g", "b", "m", "k"]
  format_cycle = ["x", "+", ".", "*"]
  price_formats = {}
  for i, p in enumerate(all_prices):
    price_formats[p] = format_cycle[i]
  # Plot linear functions
  linear_keys = list(linear_function_data.keys())
  linear_keys.sort()
  for i, func_args in enumerate(linear_keys):
    y_intercept, x_intercept = [float(k) for k in func_args.split(",")]
    x_intercept /= 60
    slope = -1 * y_intercept / x_intercept
    x = np.arange(0, x_intercept)
    y = slope * x + y_intercept
    ax = axes[i][0]
    if i == len(axes) / 2:
      ax.set_ylabel("Utility ($)", fontsize=28, labelpad=40)
    ax.tick_params(axis='both', which='both', labelsize=18)
    ax.xaxis.set_major_locator(plt.MaxNLocator(5))
    ax.yaxis.set_major_locator(plt.MaxNLocator(5))
    ax.errorbar(x, y, fmt="-", linewidth=6, color=color_cycle[i])
    for price, total_time in linear_function_data[func_args]:
      total_time /= 60
      ax.errorbar(total_time, y[total_time], fmt=price_formats[price],
        color="k", markersize=36, markeredgewidth=6, markeredgecolor="k")
  # Plot step functions
  # Currently his only handles one step!
  step_keys = list(step_function_data.keys())
  step_keys.sort(reverse=True)
  for i, func_args in enumerate(step_keys):
    step_value, end_point = [float(k) for k in func_args.split(":")]
    end_point = int(end_point / 60)
    ax = axes[i][1]
    ax.tick_params(axis='both', which='both', labelsize=18)
    ax.xaxis.set_major_locator(plt.MaxNLocator(5))
    ax.set_yticks(np.arange(0, step_value + 1, step_value / 5))
    x1 = np.arange(0, end_point)
    x2 = np.arange(end_point, end_point * 3)
    y1 = [step_value] * int(end_point)
    y2 = [0] * int(end_point) * 2
    ax.errorbar(x1, y1, fmt="-", linewidth=6, color=color_cycle[i])
    ax.errorbar(x2, y2, fmt="-", linewidth=6, color=color_cycle[i])
    ax.vlines(end_point, ymin=0, ymax=step_value, linestyle="dashed")
    ax.set_ylim([step_value * -0.2, step_value * 1.2])
    for price, total_time in step_function_data[func_args]:
      total_time = int(total_time / 60)
      if total_time == end_point:
        total_time = end_point - 1
      y = y1[total_time] if total_time < end_point else y2[total_time - end_point]
      ax.errorbar(total_time, y, fmt=price_formats[price],
        color="k", markersize=36, markeredgewidth=6, markeredgecolor="k")

  # Tweak figure layout and save
  plt.figtext(0.55, -0.03,"Expected completion time (min)", va="center", ha="center", size=28)
  legend_lines = []
  legend_labels = []
  all_prices.sort()
  for price in all_prices:
    legend_lines.append(Line2D([0], [0], color="k", linewidth=0,
      markersize=18, markeredgewidth=6, marker=price_formats[price]))
    legend_labels.append("$%s/hr" % price)
  fig.legend(tuple(legend_lines), tuple(legend_labels), "center",
    prop={"size":18}, bbox_to_anchor=(0.52, 1.08), numpoints=1, ncol=len(legend_lines), handletextpad=0.1)
  fig.set_size_inches(10, 10)
  fig.set_tight_layout({"pad": 2.5})
  fig.savefig(out_file, bbox_inches="tight")
  print("Wrote to %s." % out_file)

def main():
  args = sys.argv
  if len(args) < 2:
    print("Usage: plot_utility.py [log_dir1] <[log_dir2] ...>")
    print("  e.g. ./plot_utility.py data/linear-* data/step-*")
    sys.exit(1)
  log_dirs = [d for d in args[1:] if "tgz" not in d]
  plot(log_dirs)

if __name__ == "__main__":
  main()


