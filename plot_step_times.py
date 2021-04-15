#!/usr/bin/env python3

import itertools

import numpy as np
import matplotlib.pyplot as plt

def plot():
  fig = plt.figure(figsize=(3.25, 2.75))
  ax = fig.add_subplot(1, 1, 1)
  ax.margins(0.2, 0)
  output_file = "het_step_times.pdf"

  # Data
  batch_size = 8192
  even = batch_size / np.array([978.248])
  uneven = batch_size / np.array([1745.47])

  # Bar indexes
  width = 0.1
  i1 = list(range(len(even)))
  i2 = [x + width for x in i1]
 
  # Plot the bars
  bars = []
  ax.bar([0], even, width=width, edgecolor="white", label="2048:2048 BS", hatch="//")
  ax.bar([0.125], uneven, width=width, edgecolor="white", label="3072:1024 BS")

  # Legends and labels
  plt.xticks([0, 0.125], ["even", "uneven"], fontsize=14)
  plt.yticks(fontsize=14)
  plt.ylim((0, max(even[0], uneven[0]) * 1.2))
  ax.set_ylabel("Step time (s)", fontsize=16, labelpad=10)
  ax.legend(fontsize=14, loc='lower center', bbox_to_anchor=(0.5, 1), ncol=1, borderaxespad=1.2)
  fig.set_tight_layout({"pad": 1.5})
  fig.savefig(output_file)
  print("Saved to %s" % output_file)

if __name__ == "__main__":
  plot()

