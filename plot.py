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

GLOBAL_BATCH_SIZE = 1024
NUM_TOTAL_STEPS = 48 * 100
DOLLARS_PER_SECOND = 0.768 / 3600
MAX_NUM_WORKERS = 40

# Plot one experiment identified by the given name
# ax1 is intended for plotting throughput and ax2 for step times
def plot_experiment(ax1, ax2, experiment_name, per_worker):
  experiment_dir = "data/%s" % experiment_name
  # Parse
  throughput_name = "throughput_per_worker" if per_worker else "throughput"
  num_workers, throughputs = parse.parse_dir(experiment_dir, value_to_parse=throughput_name)
  _, step_times = parse.parse_dir(experiment_dir, value_to_parse="step_time")
  num_workers = num_workers[:MAX_NUM_WORKERS]
  throughputs = throughputs[:MAX_NUM_WORKERS]
  step_times = step_times[:MAX_NUM_WORKERS]
  # Calculate costs
  perfect_throughputs = throughputs[0] / num_workers[0] * np.array(num_workers)
  perfect_step_times = GLOBAL_BATCH_SIZE / np.array(perfect_throughputs)
  total_costs = np.array(num_workers) * np.array(step_times) *\
    NUM_TOTAL_STEPS * DOLLARS_PER_SECOND
  perfect_total_costs = np.array(num_workers) * np.array(perfect_step_times) *\
    NUM_TOTAL_STEPS * DOLLARS_PER_SECOND
  # Plot
  throughput_line = ax1.errorbar(num_workers, throughputs,\
    fmt="-x", color="b", linewidth=2, markeredgewidth=2, markersize=10)
  total_cost_line = ax2.errorbar(num_workers, total_costs,\
    fmt="-o", color="g", linewidth=2, markeredgewidth=0, markersize=10)
  if not per_worker:
    perfect_throughput_line = ax1.errorbar(num_workers, perfect_throughputs,\
      fmt="--", color="b", linewidth=1)
    #perfect_total_cost_line = ax2.errorbar(num_workers, perfect_total_costs,\
    #  fmt="--", color="g", linewidth=1)
  # Labels
  throughput_name = throughput_name.replace("_", " ").capitalize()
  labels = ["Total cost", throughput_name]
  lines = [total_cost_line, throughput_line]
  if not per_worker:
    labels.append("%s perfect scaling" % throughput_name)
    lines.append(perfect_throughput_line)
    #lines.append(perfect_total_cost_line)
  ax1.legend(lines, labels, fontsize=20, bbox_to_anchor=(0,1.05,1,0.2), loc="lower left")

# Actually plot it
def do_plot(experiment_name, per_worker):
  out_file = "output/%s.pdf" % experiment_name
  fig = plt.figure()
  plt.xticks(fontsize=20)
  plt.yticks(fontsize=20)
  ax1 = fig.add_subplot(1, 1, 1)
  ax1.set_xlabel("Number of workers", fontsize=24, labelpad=15)
  ax1.set_ylabel("Average throughput (img/s)", fontsize=24, labelpad=15)
  ax2 = ax1.twinx()
  ax2.set_ylabel("Total cost ($)", fontsize=24, labelpad=15)
  plot_experiment(ax1, ax2, experiment_name, per_worker)
  plt.xlim(xmin=1)
  plt.xticks(fontsize=20)
  plt.yticks(fontsize=20)
  fig.set_tight_layout({"pad": 1.5})
  fig.savefig(out_file, bbox_inches="tight")
  print("Wrote to %s." % out_file)

def main():
  args = sys.argv
  if len(args) < 2 or len(args) > 3:
    print("Usage: plot.py [experiment_name] <plot_throughput_per_worker>")
    sys.exit(1)
  experiment_name = args[1].lstrip("data/").rstrip("/")
  per_worker = json.loads(args[2].lower()) if len(args) == 3 else False
  do_plot(experiment_name, per_worker)

if __name__ == "__main__":
  main()

