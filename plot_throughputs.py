#!/usr/bin/env python3

import os
import re
import sys

import matplotlib.pyplot as plt
import numpy as np

def plot(input_file):
  output_file = os.getenv("OUTPUT_FILE",\
    os.path.join(*input_file.rstrip("/").split("/")[:-1], "throughputs.pdf"))

  title = os.getenv("TITLE")
  fig = plt.figure()
  ax = fig.add_subplot(1, 1, 1)
  ax.set_xlabel("Batch size", fontsize=20, labelpad=10)
  ax.set_ylabel("Throughput (ex/s)", fontsize=20, labelpad=10)

  batch_sizes = []
  throughputs = []
  with open(input_file) as f:
    for line in f.readlines():
      batch_size, throughput = tuple(line.split(" "))
      batch_sizes.append(int(batch_size))
      throughputs.append(float(throughput))
    ax.plot(batch_sizes, throughputs, linewidth=2, marker="x", markeredgewidth=2)
  ax.set_xticks([batch_sizes[0]] + batch_sizes[7:])
  plt.xticks(fontsize=14, rotation=45)
  plt.yticks(fontsize=14)
  if title is not None:
    plt.title(title, fontsize=24, pad=15)
  fig.set_tight_layout({"pad": 1.5})
  fig.savefig(output_file, bbox_inches="tight")
  print("Saved to %s" % output_file)

def main():
  args = sys.argv
  if len(args) != 2:
    print("Usage: ./plot_throughputs.py [heterogeneous_profile.txt]")
    sys.exit(1)
  plot(args[1])

if __name__ == "__main__":
  main()

