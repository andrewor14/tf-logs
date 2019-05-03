#!/usr/bin/env python

import matplotlib
import matplotlib.pyplot as plt

import math
import os
import re
import sys

import parse


# Plot one experiment identified by the given name
# ax1 is intended for plotting averages and ax2 for variances
def plot_experiment(ax1, ax2, experiment_name, mode):
  averages = {} # num workers -> averages
  variances = {} # num workers -> variances
  experiment_dir = "data/%s" % experiment_name
  for log_dir in os.listdir(experiment_dir):
    num_workers = int(re.match(".*horovod.*_(\d+)workers", log_dir).groups()[0])
    if num_workers not in averages:
      averages[num_workers] = []
    if num_workers not in variances:
      variances[num_workers] = []
    log_dir = os.path.join(experiment_dir, log_dir)
    (average, variance) = parse_average_and_variance(experiment_name, mode, log_dir)
    averages[num_workers].append(average)
    variances[num_workers].append(variance)
  (avg_x_data, avg_y_data, avg_y_min, avg_y_max) = extract_plot_data(averages)
  (var_x_data, var_y_data, _, _) = extract_plot_data(variances)
  ax1.set_xticks(avg_x_data)
  line1 = ax1.errorbar(avg_x_data, avg_y_data, yerr=[avg_y_min, avg_y_max], fmt="-x", color="b", linewidth=2)
  line2 = ax2.errorbar(var_x_data, var_y_data, fmt="--", color="g")
  ax1.legend([line1, line2], ["average", "variance"], loc="lower right")

# Parse the average and variance of the metric specified by mode
# Return a 2-tuple of (average, variance)
def parse_average_and_variance(experiment_name, mode, log_dir):
  if mode == "step":
    return parse.get_step_time_average_and_variance(log_dir)
  elif mode == "communication":
    tag = "Const" if "fake-allreduce" in experiment_name else "AddN"
    return parse.get_allreduce_time_average_and_variance(log_dir, tag)
  else:
    raise ValueError("Error: mode must be either 'step' or 'communication' (was '%s')" % mode)

# Return x, y, y_min and y_max for the specified data, which has the format {key -> [list of values]}
def extract_plot_data(data):
  # Flatten data: average by key + include min and max
  for k, v in data.items():
    data[k] = (sum(v) / len(v), min(v), max(v))
  # Sort and separate
  data = data.items()
  data.sort()
  x_data, y_data, y_lower, y_upper = [], [], [], []
  for (x, (y, y_min, y_max)) in data:
    x_data.append(x)
    y_data.append(y)
    y_lower.append(y - y_min)
    y_upper.append(y_max - y)
  return (x_data, y_data, y_lower, y_upper)

# Actually plot it
def do_plot(experiment_name, mode):
  out_file = "output/%s-%s-times.pdf" % (experiment_name, mode)
  fig = plt.figure()
  ax1 = fig.add_subplot(1, 1, 1)
  ax1.set_xlabel("num workers")
  ax1.set_ylabel("average (s)")
  ax1.set_title("horovod %s time (%s)" % (mode, experiment_name))
  ax2 = ax1.twinx()
  ax2.set_ylabel("variance")
  plot_experiment(ax1, ax2, experiment_name, mode)
  fig.set_tight_layout({"pad": 1.5})
  fig.savefig(out_file)
  print("Wrote to %s." % out_file)

def main():
  args = sys.argv
  if len(args) != 3:
    print("Usage: plot.py [mode] [experiment_name] (where mode = 'step', 'communication', or 'all')")
    sys.exit(1)
  mode = args[1]
  experiment_name = args[2]
  if mode == "all":
    do_plot(experiment_name, "step")
    do_plot(experiment_name, "communication")
  else:
    do_plot(experiment_name, mode)

if __name__ == "__main__":
  main()

