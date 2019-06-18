#!/usr/bin/env python

import matplotlib
import matplotlib.pyplot as plt

import math
import os
import re
import sys

import parse


PLOT_THROUGHPUT_PER_WORKER = False

# Plot one experiment identified by the given name
# ax1 is intended for plotting throughput and ax2 for step times
def plot_experiment(ax1, ax2, experiment_name):
  experiment_dir = "data/%s" % experiment_name
  # Parse
  num_workers, throughputs = parse.parse_dir(experiment_dir, value_to_parse="throughput")
  _, throughputs_per_worker = parse.parse_dir(experiment_dir, value_to_parse="throughput_per_worker")
  _, step_times = parse.parse_dir(experiment_dir, value_to_parse="step_time")
  # Plot
  throughput_line = ax1.errorbar(num_workers, throughputs,\
    fmt="-x", color="r", linewidth=2, markeredgewidth=2, markersize=10)
  step_time_line = ax2.errorbar(num_workers, step_times,\
    fmt="-+", color="g", linewidth=2, markeredgewidth=2, markersize=10)
  # Labels
  if PLOT_THROUGHPUT_PER_WORKER:
    throughput_per_worker_line = ax1.errorbar(num_workers, throughputs_per_worker,\
      fmt="-o", color="b", linewidth=2, markeredgewidth=2, markersize=10)
    lines = [throughput_line, throughput_per_worker_line, step_time_line]
    labels = ["throughput", "throughput per worker", "step time"]
  else:
    lines = [throughput_line, step_time_line]
    labels = ["throughput", "step time"]
  ax1.legend(lines, labels, loc="best")

# Actually plot it
def do_plot(experiment_name):
  out_file = "output/%s.pdf" % experiment_name
  fig = plt.figure()
  ax1 = fig.add_subplot(1, 1, 1)
  ax1.set_xlabel("num workers")
  ax1.set_ylabel("throughput (img/s)")
  ax1.set_title("autoscaling %s" % experiment_name)
  ax2 = ax1.twinx()
  ax2.set_ylabel("step time (s)")
  plot_experiment(ax1, ax2, experiment_name)
  fig.set_tight_layout({"pad": 1.5})
  fig.savefig(out_file)
  print("Wrote to %s." % out_file)

def main():
  args = sys.argv
  if len(args) != 2:
    print("Usage: plot.py [experiment_name]")
    sys.exit(1)
  experiment_name = args[1]
  do_plot(experiment_name)

if __name__ == "__main__":
  main()

