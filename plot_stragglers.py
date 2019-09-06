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

MAX_NUM_WORKERS = 50

# Plot one experiment identified by the given name
def plot_experiment(ax, experiment_name, perfect_scaling=False):
  experiment_dir = "data/%s" % experiment_name
  # Parse
  throughput_name = "throughput"
  num_workers, throughputs = parse.parse_dir(experiment_dir, value_to_parse=throughput_name)
  num_workers = num_workers[:MAX_NUM_WORKERS]
  throughputs = throughputs[:MAX_NUM_WORKERS]
  # Labels
  split = experiment_name.split("-")
  multiplier = round(1 / float(split[1]), 2)
  replaced = "replaced" if "replace" in experiment_name else "straggler"
  label = "%sx %s" % (multiplier, replaced)
  fmt = None
  color = None
  if "straggler-2" in experiment_name:
    color="r"
  elif "straggler-1.3" in experiment_name:
    color="b"
  if "replace" in experiment_name:
    fmt="-"
  else:
    fmt="--"
  ax.errorbar(num_workers, throughputs,\
    fmt=fmt, linewidth=4, markeredgewidth=4, markersize=15, color=color, label=label)
  # Maybe add perfect scaling line
  if perfect_scaling:
    perfect_scaling_throughput = None
    perfect_scaling_throughput = throughputs[0] / num_workers[0] * np.array(num_workers)
    ax.errorbar(num_workers, perfect_scaling_throughput,\
      fmt="--", color="black", linewidth=1, label="perfect scaling")

# Actually plot it
def do_plot(experiment_names):
  out_file = "output/stragglers_eval.pdf"
  fig = plt.figure()
  ax = fig.add_subplot(1, 1, 1)
  plt.xticks(fontsize=20)
  plt.yticks(fontsize=20)
  ax.set_xlabel("Number of workers", fontsize=24, labelpad=15)
  ax.set_ylabel("Average throughput (img/s)", fontsize=24, labelpad=15)
  for i, e in enumerate(experiment_names):
    print(e)
    e = e.lstrip("data/").rstrip("/")
    plot_experiment(ax, e)
  plt.xlim(xmin=1)
  ax.legend(fontsize=24, loc="center", bbox_to_anchor=(1.35, 0.5))
  fig.set_tight_layout({"pad": 1.5})
  fig.savefig(out_file, bbox_inches="tight")
  print("Wrote to %s." % out_file)

def main():
  args = sys.argv
  if len(args) < 2:
    print("Usage: plot_stragglers.py [experiment_name1] <[experiment_name2] ...>")
    print("  (e.g. ./plot_stragglers.py data/*straggler*)")
    sys.exit(1)
  experiment_names = [x for x in args[1:] if "tgz" not in x]
  do_plot(experiment_names)

if __name__ == "__main__":
  main()

