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

MAX_NUM_WORKERS = 16

# Plot one experiment identified by the given name
def plot_experiment(ax, experiment_name, per_worker, perfect_scaling=False):
  experiment_dir = "data/%s" % experiment_name
  # Parse
  throughput_name = "throughput_per_worker" if per_worker else "throughput"
  num_workers, throughputs = parse.parse_dir(experiment_dir, value_to_parse=throughput_name)
  num_workers = num_workers[:MAX_NUM_WORKERS]
  throughputs = throughputs[:MAX_NUM_WORKERS]
  experiment_name = experiment_name.lstrip("cifar10-60workers-")
  # Labels
  label = None
  fmt = None
  if "no-stragglers" in experiment_name:
    label = "No stragglers"
    fmt = "-x"
  else:
    label = "1 straggler"
    fmt = "-+"
  ax.errorbar(num_workers, throughputs,\
    fmt=fmt, linewidth=2, markeredgewidth=4, markersize=15, label=label)
  # Maybe add perfect scaling line
  if perfect_scaling:
    perfect_scaling_throughput = None
    if per_worker:
      perfect_scaling_throughput = [throughputs[0]] * len(num_workers)
    else:
      perfect_scaling_throughput = throughputs[0] / num_workers[0] * np.array(num_workers)
    ax.errorbar(num_workers, perfect_scaling_throughput,\
      fmt="--", color="black", linewidth=1, label="perfect scaling")

# Actually plot it
def do_plot(experiment_name, per_worker):
  out_file = "output/stragglers.pdf"
  fig = plt.figure()
  ax = fig.add_subplot(1, 1, 1)
  plt.xticks(fontsize=20)
  plt.yticks(fontsize=20)
  #gca = plt.gca()
  #gca.set_ylim([0, 800])
  #gca.set_xlim([0, 10])
  ax.set_xlabel("Number of workers", fontsize=24, labelpad=15)
  ax.set_ylabel("Average throughput (img/s)", fontsize=24, labelpad=15)
  for i, e in enumerate(experiment_name.split(",")):
    e = e.lstrip("data/").rstrip("/")
    plot_experiment(ax, e, per_worker)
  plt.xlim(xmin=1)
  ax.legend(loc="best", fontsize=24)
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

