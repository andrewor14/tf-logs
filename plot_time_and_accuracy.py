#!/usr/bin/env python3

import os
import re
import sys

import matplotlib.pyplot as plt
import numpy as np

def plot(output_path, ylabel, vals1, vals2):
  fig = plt.figure(figsize=(7, 3))
  ax = fig.add_subplot(1, 1, 1)
  ax.margins(0.1, 0.2)
  bar_width = 0.35
  labels = ["Job %s" % i for i in range(3)]
  r1 = np.arange(len(vals1))
  r2 = [x + bar_width for x in r1]
  # Make the plot
  bars1 = ax.bar(r1, vals1, color="mediumturquoise", width=bar_width, edgecolor='white', label='var1')
  bars2 = ax.bar(r2, vals2, color="tomato", width=bar_width, edgecolor='white', label='var2')
  # Add values on the top
  label_values = [v for v in vals1 + vals2]
  for i, rect in enumerate(bars1 + bars2):
    plt.text(rect.get_x() + rect.get_width() / 2.0, rect.get_height(),\
      "%.2g" % label_values[i], ha='center', va='bottom', size=14)
  # Legend
  box = ax.get_position()
  ax.set_position([box.x0, box.y0, box.width, box.height * 0.8])
  ax.legend(labels=["WFS", "Priority"], loc="upper center", bbox_to_anchor=(0.5, 1.5), fontsize=24, ncol=2)
  ax.set_ylabel(ylabel, fontsize=28, labelpad=10)
  plt.xticks([r + bar_width/2 for r in range(len(vals1))], labels, fontsize=28)
  plt.yticks(fontsize=20)
  fig.set_tight_layout({"pad": 1.5})
  fig.savefig(output_path, bbox_inches="tight")
  print("Wrote to %s" % output_path)

def main():
  vals1 = [0.9186, 0.933, 0.8856]
  vals2 = [0.922, 0.932, 0.9057]
  plot("9-7/elasticity-3jobs-accuracy.pdf", "Val accuracy", vals1, vals2)
  vals1 = [1262, 2025, 1562]
  vals2 = [928, 2594, 3152]
  vals1 = [v / 60 for v in vals1]
  vals2 = [v / 60 for v in vals2]
  plot("9-7/elasticity-3jobs-jct.pdf", "JCT (min)", vals1, vals2)

if __name__ == "__main__":
  main()

