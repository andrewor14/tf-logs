#!/usr/bin/env python

import matplotlib
import matplotlib.pyplot as plt
import numpy as np

import math
import json
import os
import re
import sys

import parse


# Plot one experiment identified by the given name
# ax1 is intended for plotting throughput and ax2 for step times
def plot_experiment(ax1, ax2, experiment_name, per_worker):
  experiment_dir = "data/%s" % experiment_name
  # Parse
  throughput_name = "throughput_per_worker" if per_worker else "throughput"
  num_workers, throughputs = parse.parse_dir(experiment_dir, value_to_parse=throughput_name)
  _, step_times = parse.parse_dir(experiment_dir, value_to_parse="step_time")
  # Plot
  throughput_line = ax1.errorbar(num_workers, throughputs,\
    fmt="-x", color="b", linewidth=2, markeredgewidth=2, markersize=10)
  step_time_line = ax2.errorbar(num_workers, step_times,\
    fmt="-+", color="g", linewidth=2, markeredgewidth=2, markersize=10)
  # Add perfect scaling line
  perfect_scaling_throughput = None
  if per_worker:
    perfect_scaling_throughput = [throughputs[0]] * len(num_workers)
  else:
    perfect_scaling_throughput = throughputs[0] / num_workers[0] * np.array(num_workers)
  perfect_scaling_throughput_line = ax1.errorbar(num_workers, perfect_scaling_throughput,\
    fmt="--", color="b", linewidth=1)
  # Labels
  throughput_name = throughput_name.replace("_", " ")
  labels = [throughput_name, throughput_name + " perfect scaling", "step time"]
  legend_location = "upper right" if per_worker else "upper center"
  ax1.legend([throughput_line, perfect_scaling_throughput_line, step_time_line], labels, loc=legend_location)

# Actually plot it
def do_plot(experiment_name, per_worker):
  out_file = "output/%s.pdf" % experiment_name
  fig = plt.figure()
  ax1 = fig.add_subplot(1, 1, 1)
  ax1.set_xlabel("num workers")
  ax1.set_ylabel("throughput (img/s)")
  ax1.set_title("autoscaling %s" % experiment_name)
  ax2 = ax1.twinx()
  ax2.set_ylabel("step time (s)")
  plot_experiment(ax1, ax2, experiment_name, per_worker)
  plt.xlim(xmin=1)
  fig.set_tight_layout({"pad": 1.5})
  fig.savefig(out_file)
  print("Wrote to %s." % out_file)

def main():
  args = sys.argv
  if len(args) < 2 or len(args) > 3:
    print("Usage: plot.py [experiment_name] <plot_throughput_per_worker>")
    sys.exit(1)
  experiment_name = args[1]
  per_worker = json.loads(args[2].lower()) if len(args) == 3 else False
  do_plot(experiment_name, per_worker)

if __name__ == "__main__":
  main()

