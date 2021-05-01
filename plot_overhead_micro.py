#!/usr/bin/env python3

import numpy as np
import matplotlib.pyplot as plt

def main():
  width = 0.125
  labels = ["ResNet-50", "Transformer", "BERT-LARGE"]
  output_file = "output/overhead-microbenchmark.pdf"

  _tf1 = np.array([1, 1, 1])
  _tf2 = np.array([1, 1, 1])
  _tf3 = np.array([1, 1, 1])
  _tf4 = np.array([1, 1, 1])
  _vf1 = np.array([1, 1, 1]) / _tf1
  _vf2 = np.array([1, 1, 1]) / _tf2
  _vf3 = np.array([1, 1, 1]) / _tf3
  _vf4 = np.array([1, 1, 1]) / _tf4
  ylabel = "Norm. \nthroughput"

  p0 = np.arange(len(_vf1))
  p1 = [x + width for x in p0]
  p2 = [x + width for x in p1]
  p3 = [x + width for x in p2]
  p4 = [x + width for x in p3]
  
  fig = plt.figure(figsize=(6, 2.75))
  ax = fig.add_subplot(1, 1, 1)
  ax.margins(0.1, 0)

  colors = iter(plt.get_cmap("Set3").colors[3:])
  ax.bar(p1, _vf1, color=next(colors), width=width, edgecolor="white", label="1.0 max batch size", hatch="/")
  ax.bar(p2, _vf2, color=next(colors), width=width, edgecolor="white", label="0.5 max batch size", hatch="\\")
  ax.bar(p3, _vf3, color=next(colors), width=width, edgecolor="white", label="0.25 max batch size", hatch=".")
  ax.bar(p4, _vf4, color=next(colors), width=width, edgecolor="white", label="0.125 max batch size")
  plt.axhline(y=1, color="black", linestyle='--')
 
  ax.set_ylabel(ylabel, fontsize=16, labelpad=15)

  plt.xticks([p + 2.5 * width for p in range(len(_vf1))], labels, fontsize=16)
  plt.yticks([0.0, 0.2, 0.4, 0.6, 0.8, 1.0], fontsize=14)
  ax.legend(fontsize=12, loc='lower center', bbox_to_anchor=(0.5, 1.05), ncol=2)
  plt.ylim(0, 1.2)
  fig.set_tight_layout({"pad": 1.5})
  fig.savefig(output_file)
  print("Saved to %s" % output_file)

if __name__ == "__main__":
  main()

