#!/usr/bin/env python3

import itertools

import numpy as np
import matplotlib.pyplot as plt

def plot():
  fig = plt.figure(figsize=(6.5, 3))
  ax = fig.add_subplot(1, 1, 1)
  ax.margins(0.1, 0)
  output_file = "het_throughputs.pdf"

  # Data
  labels = ["H1 (a,b,c)", "H2 (a,b,c,d)", "H3"]
  v = np.array([1969] * 3)
  p = np.array([532.657, 1013.14, 1838.94])
  ha = np.array([978.248, 2139.48, 2803.32])
  hb = np.array([1745.47, 2054.21])
  hc = np.array([1745.58, 2169.04])
  hd = np.array([-1, 2174.31])

  # Bar indexes
  width = 0.125
  i1 = list(range(len(v)))
  i2 = [x + width for x in i1]
  i3 = [x + width for x in i2]
  i4 = [x + width for x in i3[:2]]
  i5 = [x + width for x in i4]
  i6 = [x + width for x in i5]
  # Shift groups 2 onwards to the left by 1 bar
  for i in [i1, i2, i3, i4, i5, i6]:
    for g in range(1, len(i)):
      i[g] -= width
  
  # Plot the bars
  colors = iter(plt.get_cmap("Set2").colors)
  bars = []
  ax.bar(i1, v, color=next(colors), width=width, edgecolor="white", label="V2", hatch="//")
  p_color = next(colors)
  ax.bar([i2[0]], [p[0]], color=p_color, width=width, edgecolor="white", label="P2", hatch="\\\\")
  ax.bar([i2[1]], [p[1]], color=p_color, width=width, edgecolor="white", label="P4", hatch=".")
  ax.bar([i2[2]], [p[2]], color=p_color, width=width, edgecolor="white", label="P8", hatch="x")
  b3 = ax.bar(i3, ha, color=next(colors), width=width, edgecolor="white")
  b4 = ax.bar(i4, hb, color=next(colors), width=width, edgecolor="white")
  b5 = ax.bar(i5, hc, color=next(colors), width=width, edgecolor="white")
  b6 = ax.bar(i6, hd, color=next(colors), width=width, edgecolor="white")

  # Plot horizontal dotted line for comparison
  plt.axhline(y=max(v[0], p[0]), xmin=0.075, xmax=0.325, color="black", linestyle='--')
  plt.axhline(y=max(v[1], p[1]), xmin=0.4, xmax=0.7, color="black", linestyle='--')
  plt.axhline(y=max(v[2], p[2]), xmin=0.775, xmax=0.925, color="black", linestyle='--')

  # Add improvement multiplier above the best bar for each group
  mult1 = max(ha[0], hb[0], hc[0], hd[0]) / max(v[0], p[0])
  mult2 = max(ha[1], hb[1], hc[1], hd[1]) / max(v[1], p[1])
  mult3 = ha[2] / max(v[2], p[2])
  mults = [mult1, mult2, mult3]
  rects = [b5.patches[0], b6.patches[1], b3.patches[2]]
  for i in range(len(mults)):
    if mults[i] < 1:
      continue
    plt.text(rects[i].get_x() + rects[i].get_width() / 2.0, rects[i].get_height() + 100,\
      "%.2fx" % mults[i], ha='center', va='bottom', fontsize=12)

  # Legends and labels
  plt.text(b3.patches[0].get_x() - width * 1.55, -555, "H1(", fontsize=16)
  plt.text(b5.patches[0].get_x() + width * 0.8, -555, ")", fontsize=16)
  plt.text(b3.patches[1].get_x() - width * 1.55, -555, "H2(", fontsize=16)
  plt.text(b6.patches[1].get_x() + width * 0.8, -555, ")", fontsize=16)
  plt.xticks([0.25, 0.375, 0.5, 1.125, 1.25, 1.375, 1.5, 2.125], ["a", "b", "c", "a", "b", "c", "d", "H3"], fontsize=16)
  plt.yticks(fontsize=16)
  plt.ylim(0, max(itertools.chain.from_iterable([v, p, ha, hb, hc, hd])) * 1.25)
  ax.set_ylabel("Throughput (img/s)", fontsize=16, labelpad=15)
  ax.legend(fontsize=14, loc='lower center', bbox_to_anchor=(0.5, 1.05), ncol=4)
  fig.set_tight_layout({"pad": 1.5})
  fig.savefig(output_file)
  print("Saved to %s" % output_file)

if __name__ == "__main__":
  plot()

