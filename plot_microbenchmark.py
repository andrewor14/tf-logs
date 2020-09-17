#!/usr/bin/env python3

import numpy as np
import matplotlib.pyplot as plt

def plot(metric):
  width = 0.1
  labels = ["ResNet-50", "Transformer", "BERT-LARGE"]
  output_file = "output/%s-microbenchmark.pdf" % metric

  if metric == "memory":
    _1vn = np.array([8.81, 8.66, 7.60])
    _2vn = np.array([8.90, 9.51, 8.93]) / _1vn
    _4vn = np.array([8.90, 9.64, 8.93]) / _1vn
    _8vn = np.array([8.90, 9.64, 8.93]) / _1vn
    _16vn = np.array([8.90, 9.69, 8.93]) / _1vn
    _32vn = np.array([8.90, 9.69, 8.93]) / _1vn
    _1vn /= _1vn
    ylabel = "Norm. peak memory"
  elif metric == "throughput":
    _1vn = np.array([523.682, 6703.43, 22.4188])
    _2vn = np.array([545.178, 6863.33, 25.1946]) / _1vn
    _4vn = np.array([551.58, 6963.69, 27.4218]) / _1vn
    _8vn = np.array([533.817, 7003.52, 28.5995]) / _1vn
    _16vn = np.array([551.441, 7020.67, 28.8711]) / _1vn
    _32vn = np.array([542.65, 7036.4, 29.4659]) / _1vn
    _1vn /= _1vn
    ylabel = "Norm. throughput"
  else:
    raise ValueError("Unrecognized metric '%s'" % metric)

  p1 = np.arange(len(_1vn))
  p2 = [x + width for x in p1]
  p3 = [x + width for x in p2]
  p4 = [x + width for x in p3]
  p5 = [x + width for x in p4]
  p6 = [x + width for x in p5]
  
  fig = plt.figure(figsize=(6, 3))
  ax = fig.add_subplot(1, 1, 1)
  ax.margins(0.1, 0)

  colors = iter(plt.get_cmap("Set3").colors[2:])
  ax.bar(p1, _1vn, color=next(colors), width=width, edgecolor="white", label="TF", hatch="//")
  ax.bar(p2, _2vn, color=next(colors), width=width, edgecolor="white", label="VF (2VN)")
  ax.bar(p3, _4vn, color=next(colors), width=width, edgecolor="white", label="VF (4VN)")
  ax.bar(p4, _8vn, color=next(colors), width=width, edgecolor="white", label="VF (8VN)")
  ax.bar(p5, _16vn, color=next(colors), width=width, edgecolor="white", label="VF (16VN)")
  ax.bar(p6, _32vn, color=next(colors), width=width, edgecolor="white", label="VF (32VN)")
  plt.axhline(y=1, color="black", linestyle='--')
 
  ax.set_ylabel(ylabel, fontsize=16, labelpad=15)
  plt.xticks([p + 2.5 * width for p in range(len(_2vn))], labels, fontsize=16)
  plt.yticks([0.0, 0.2, 0.4, 0.6, 0.8, 1.0, 1.2], fontsize=16)
  plt.ylim(0, 1.35)
  ax.legend(fontsize=12, loc='lower center', bbox_to_anchor=(0.5, 1.05), ncol=3)
  fig.set_tight_layout({"pad": 1.5})
  fig.savefig(output_file)
  print("Saved to %s" % output_file)

def main():
  plot("memory")
  plot("throughput")

if __name__ == "__main__":
  main()

