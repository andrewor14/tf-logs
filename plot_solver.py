#!/usr/bin/env python3

import itertools

import numpy as np
import matplotlib.pyplot as plt

def plot():
  fig = plt.figure(figsize=(6, 2))
  ax = fig.add_subplot(1, 1, 1)
  output_file = "solver_throughputs.pdf"

  # Data
  labels = ["H1a", "H1b", "H1c", "H2a", "H2b", "H2c", "H2d", "H3"]
  real = [978.248, 1745.47, 1745.58, 2139.48, 2054.21, 2169.04, 2174.31, 2803.32]
  solver = [987.8936030635327, 1751.6295299410606, 1751.6295299410606, 2169.308108957865,\
    2169.308108957865, 2169.308108957865, 2169.308108957865, 2855.3636916044975]

  # Bar indexes
  width = 0.3
  i1 = list(range(len(real)))
  i2 = [x + width for x in i1]
  
  # Plot the bars
  bars = []
  ax.bar(i1, real, color="tab:red", width=width, label="Actual")
  ax.bar(i2, solver, color="lightskyblue", width=width, label="Solver")

  # Legends and labels
  plt.xticks([width/2 + x for x in i1], labels, fontsize=12)
  plt.yticks(fontsize=12)
  plt.ylim(0, max(real + solver) * 1.1)
  ax.set_ylabel("Throughput (img/s)", fontsize=14.5)
  ax.yaxis.set_label_coords(-0.15, 0.425)
  ax.legend(fontsize=12, loc="upper left", ncol=2)
  fig.set_tight_layout({"pad": 1})
  fig.savefig(output_file)
  print("Saved to %s" % output_file)

  diffs = []
  for i in range(len(real)):
    diffs.append(abs(solver[i] - real[i]) / real[i] * 100)
    print("Percent difference: %.3g%%" % diffs[-1])
  print("Average percent difference: %.3g%%" % (sum(diffs) / len(diffs)))

if __name__ == "__main__":
  plot()

