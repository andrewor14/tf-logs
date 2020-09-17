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
    value = "{:.3f}".format(label_values[i]) if "accuracy" in ylabel else "%.2g" % label_values[i]
    plt.text(rect.get_x() + rect.get_width() / 2.0, rect.get_height(),\
      value, ha='center', va='bottom', size=13)
  # Legend
  box = ax.get_position()
  ax.set_position([box.x0, box.y0, box.width, box.height * 0.8])
  ax.legend(labels=["VF", "Priority"], loc="upper center", bbox_to_anchor=(0.5, 1.5), fontsize=24, ncol=2)
  ax.set_ylabel(ylabel, fontsize=28, labelpad=10)
  plt.xticks([r + bar_width/2 for r in range(len(vals1))], labels, fontsize=28)
  plt.yticks(fontsize=20)
  fig.set_tight_layout({"pad": 1.5})
  fig.savefig(output_path, bbox_inches="tight")
  print("Wrote to %s" % output_path)

def main():
  vals1 = [0.9129, 0.9137, 0.8997]
  vals2 = [0.9107, 0.9175, 0.9084]
  plot("9-13/elasticity-3jobs-accuracy.pdf", "Val accuracy", vals1, vals2)
  vals1 = [610.2, 1944.5, 2491.3]
  vals2 = [590.3, 2281.9, 3944.1]
  vals1 = [v / 60 for v in vals1]
  vals2 = [v / 60 for v in vals2]
  plot("9-13/elasticity-3jobs-jct.pdf", "JCT (min)", vals1, vals2)

if __name__ == "__main__":
  main()

