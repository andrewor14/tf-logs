#!/usr/bin/env python

import os
import sys

import matplotlib.pyplot as plt
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
    parsed = parse.parse_dir(log_dir, "total_time")[1]
    if len(parsed) == 1:
      total_time = float(parsed[0])
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
  print(linear_function_data)
  # Decide how many plots to make
  # We align all the linear and step plots
  out_file = "output/utility.pdf"
  fig, axes = plt.subplots(nrows=len(linear_function_data), ncols=2)
  color_cycle = ["r", "g", "b", "m", "k"]
  format_cycle = ["x", "+", ".", "*"]
  price_formats = {}
  for i, p in enumerate(all_prices):
    price_formats[p] = format_cycle[i]
  print(price_formats)
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
    ax.errorbar(x, y, fmt="-", linewidth=4, color=color_cycle[i])
    for price, total_time in linear_function_data[func_args]:
      total_time /= 60
      ax.errorbar(total_time, y[total_time], fmt=price_formats[price],
        color=color_cycle[i], markersize=36, markeredgewidth=8, markeredgecolor=color_cycle[i])
  # Plot step functions
  step_function_data = {1:1, 2:2, 3:3}
  for i, func_args in enumerate(step_function_data.keys()):
    ax = axes[i][1]
    ax.tick_params(axis='both', which='both', labelsize=18)
    ax.xaxis.set_major_locator(plt.MaxNLocator(5))
    ax.yaxis.set_major_locator(plt.MaxNLocator(5))
  plt.text(-1, -0.4, "Expected completion time (min)", fontsize=28)
  # Tweak figure layout and save
  fig.set_size_inches(10, 10)
  fig.set_tight_layout({"pad": 1.5})
  fig.savefig(out_file, bbox_inches="tight")
  print("Wrote to %s." % out_file)

def main():
  args = sys.argv
  if len(args) < 2:
    print("Usage: plot_utility.py [log_dir1] <[log_dir2] ...>")
    sys.exit(1)
  log_dirs = [d for d in args[1:] if "tgz" not in d]
  plot(log_dirs)

if __name__ == "__main__":
  main()


