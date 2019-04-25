#!/usr/bin/env python

import matplotlib
import matplotlib.pyplot as plt

import parse_step_times

import math
import os
import re
import sys

# Plot one experiment
def plot_experiment(ax1, ax2, experiment_name):
  step_time_averages = {} # num workers -> step time averages
  step_time_variances = {} # num workers -> step time variances
  for log_dir in os.listdir(experiment_name):
    num_workers = int(re.match("mpi-horovod_(\d+)workers", log_dir).groups()[0])
    if num_workers not in step_time_averages:
      step_time_averages[num_workers] = []
    if num_workers not in step_time_variances:
      step_time_variances[num_workers] = []
    log_dir = os.path.join(experiment_name, log_dir)
    (average, variance) = parse_step_times.get_step_time_average_and_variance(log_dir)
    step_time_averages[num_workers].append(average)
    step_time_variances[num_workers].append(variance)
  (avg_x_data, avg_y_data, avg_y_min, avg_y_max) = get_plot_data(step_time_averages)
  (var_x_data, var_y_data, _, _) = get_plot_data(step_time_variances)
  ax1.set_xticks(avg_x_data)
  line1 = ax1.errorbar(avg_x_data, avg_y_data, yerr=[avg_y_min, avg_y_max], fmt="-x", color="b", linewidth=2)
  line2 = ax2.errorbar(var_x_data, var_y_data, fmt="-x", color="g")
  ax1.legend([line1, line2], ["average", "variance"], loc="lower right")

# Return x, y, y_min and y_max for the specified data, which has the format {key -> [list of values]}
def get_plot_data(data):
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

# Plot it
def make_plot(experiment_name):
  out_file = "%s-step-times.pdf" % experiment_name
  fig = plt.figure()
  ax1 = fig.add_subplot(1, 1, 1)
  ax1.set_xlabel("num workers")
  ax1.set_ylabel("average (s)")
  ax1.set_title("horovod step time (%s)" % experiment_name)
  ax2 = ax1.twinx()
  ax2.set_ylabel("variance")
  plot_experiment(ax1, ax2, experiment_name)
  fig.savefig(out_file)
  print("Wrote to %s." % out_file)

def main():
  args = sys.argv
  experiment_names = []
  if len(args) > 1:
    experiment_names = args[1:]
  else:
    experiment_names = [
      "cifar10-trivial",
      "synthetic-andrew-trivial",
      "synthetic-andrew-trivial2",
      "synthetic-andrew-trivial3"]
  for name in experiment_names:
    make_plot(name)

if __name__ == "__main__":
  main()

