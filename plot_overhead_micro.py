#!/usr/bin/env python3

import numpy as np
import matplotlib.pyplot as plt

def main():
  width = 0.125
  labels = ["ResNet-50", "Transformer", "BERT-LARGE"]
  output_file = "output/overhead-microbenchmark.pdf"

  _tf1 = np.array([675.812, 3790.81, 28.3777])
  _tf2 = np.array([599.966, 5498.67, 20.2030])
  _tf3 = np.array([541.12, 6423.41, 12.7027])
  _tf4 = np.array([455.301, 6914.6, -1])
  _vf1 = np.array([710.024, 3352.58, 27.1990]) / _tf1
  _vf2 = np.array([622.701, 4988, 18.7252]) / _tf2
  _vf3 = np.array([543.769, 6042.52, 11.3639]) / _tf3
  _vf4 = np.array([438.61, 6726.52, 0]) / _tf4
  ylabel = "Norm. \nthroughput"

  p0 = np.arange(len(_vf1))
  p1 = [x + width for x in p0]
  p2 = [x + width for x in p1]
  p3 = [x + width for x in p2]
  p4 = [x + width for x in p3]
  
  fig = plt.figure(figsize=(6, 2.75))
  ax = fig.add_subplot(1, 1, 1)
  ax.margins(0.1, 0)

  colors = plt.get_cmap("Set3").colors[3:]
  color_iter = iter(colors)
  b1 = ax.bar(p1, _vf4, color=next(color_iter), width=width, edgecolor="white", label="1/8 max batch size", hatch="/")
  ax.bar(p2, _vf3, color=next(color_iter), width=width, edgecolor="white", label="1/4 max batch size", hatch="\\")
  ax.bar(p3, _vf2, color=next(color_iter), width=width, edgecolor="white", label="1/2 max batch size", hatch=".")
  ax.bar(p4, _vf1, color=next(color_iter), width=width, edgecolor="white", label="max batch size")
  plt.axhline(y=1, color="black", linestyle='--')

  plt.text(b1.patches[2].get_x() - 0.06, 0.04, "N/A", fontsize=10, color=colors[0], weight="bold")
 
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

