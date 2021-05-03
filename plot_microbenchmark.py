#!/usr/bin/env python3

import numpy as np
import matplotlib.pyplot as plt

def plot(metric):
  width = 0.1
  labels = ["ResNet-50", "Transformer", "BERT-LARGE"]
  output_file = "output/%s-microbenchmark.pdf" % metric

  if metric == "memory":
    _tf = np.array([8.81, 8.66, 7.60]) # TODO: fix
    _1vn = np.array([8.81, 8.66, 7.60]) / _tf
    _2vn = np.array([8.90, 9.51, 8.93]) / _tf
    _4vn = np.array([8.90, 9.64, 8.93]) / _tf
    _8vn = np.array([8.90, 9.64, 8.93]) / _tf
    _16vn = np.array([8.90, 9.69, 8.93]) / _tf
    _32vn = np.array([8.90, 9.69, 8.93]) / _tf
    ylabel = "Norm. \npeak memory"
  elif metric == "throughput":
    _tf = np.array([675.812, 6914.6, 28.3777])
    _1vn = np.array([710.024, 6726.52, 27.1990]) / _tf
    _2vn = np.array([725.396, 6854.53, 31.7647]) / _tf
    _4vn = np.array([719.041, 6919.18, 34.65011]) / _tf
    _8vn = np.array([722.736, 6959.5, 36.0466]) / _tf
    _16vn = np.array([721.203, 6976.23, 36.9445]) / _tf
    _32vn = np.array([715.372, 6991.22, 37.3013]) / _tf
    ylabel = "Norm. \nthroughput"
  else:
    raise ValueError("Unrecognized metric '%s'" % metric)

  p1 = np.arange(len(_1vn))
  p2 = [x + width for x in p1]
  p3 = [x + width for x in p2]
  p4 = [x + width for x in p3]
  p5 = [x + width for x in p4]
  p6 = [x + width for x in p5]
  
  if metric == "memory":
    fig = plt.figure(figsize=(6, 2.75))
  else:
    fig = plt.figure(figsize=(6, 2))
  ax = fig.add_subplot(1, 1, 1)
  ax.margins(0.1, 0)

  colors = iter(plt.get_cmap("Set3").colors[2:])
  ax.bar(p1, _1vn, color=next(colors), width=width, edgecolor="white", label="1VN")
  ax.bar(p2, _2vn, color=next(colors), width=width, edgecolor="white", label="2VN")
  ax.bar(p3, _4vn, color=next(colors), width=width, edgecolor="white", label="4VN")
  ax.bar(p4, _8vn, color=next(colors), width=width, edgecolor="white", label="8VN")
  ax.bar(p5, _16vn, color=next(colors), width=width, edgecolor="white", label="16VN")
  ax.bar(p6, _32vn, color=next(colors), width=width, edgecolor="white", label="32VN")
  plt.axhline(y=1, color="black", linestyle='--')
 
  ax.set_ylabel(ylabel, fontsize=16, labelpad=15)
  plt.xticks([p + 2.5 * width for p in range(len(_2vn))], labels, fontsize=16)
  plt.yticks([0.0, 0.2, 0.4, 0.6, 0.8, 1.0, 1.2], fontsize=14)
  plt.ylim(0, 1.35)
  if metric == "memory":
    ax.legend(fontsize=12, loc='lower center', bbox_to_anchor=(0.5, 1.05), ncol=3)
  fig.set_tight_layout({"pad": 1.5})
  fig.savefig(output_file)
  print("Saved to %s" % output_file)

def main():
  plot("memory")
  plot("throughput")

if __name__ == "__main__":
  main()

