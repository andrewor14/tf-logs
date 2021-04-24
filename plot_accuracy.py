#!/usr/bin/env python3

import os
import re
import sys

import matplotlib.pyplot as plt

def main():
  args = sys.argv
  if len(args) == 1:
    print("Usage: ./plot_accuracy.py [data1.txt] [data2.txt] [data3.txt] ...")
    print("  Each data file contains two columns: epoch and validation accuracy")
    sys.exit(1)
  data_files = args[1:]
  smooth_factor = int(os.getenv("SMOOTH_FACTOR", -1))
  title = os.getenv("TITLE", "ResNet-50 on ImageNet")
  output_file = os.getenv("OUTPUT_FILE", "output.pdf")
  data_file_prefix = os.getenv("DATA_FILE_PREFIX", "resnet-imagenet-")
  data_file_suffix = os.getenv("DATA_FILE_SUFFIX", ".txt")
  figure_size = os.getenv("FIGURE_SIZE")

  # Allow the user to plot other dimensions/units
  steps_per_epoch = int(os.getenv("STEPS_PER_EPOCH", -1))
  xlabel = "Step" if steps_per_epoch > 0 else "Epoch"
  xlabel = os.getenv("XLABEL", xlabel)
  ylabel = os.getenv("YLABEL", "Validation accuracy")
  space_xticks_apart = os.getenv("SPACE_XTICKS_APART", "").lower() == "true"
  put_legend_outside = os.getenv("PUT_LEGEND_OUTSIDE", "").lower() == "true"
  bold_baseline = os.getenv("BOLD_BASELINE", "").lower() == "true"
  plot_baseline_first = os.getenv("PLOT_BASELINE_FIRST", "").lower() == "true"
  legend_baseline_first = os.getenv("LEGEND_BASELINE_FIRST", "").lower() == "true"
  ylim = os.getenv("YLIM")
  legend_font_size = int(os.getenv("LEGEND_FONT_SIZE", "14"))
  legend_ncol = int(os.getenv("LEGEND_NCOL", "1"))
  legend_no_batch_size = os.getenv("LEGEND_NO_BATCH_SIZE", "").lower() == "true"

  # Sort the labels
  def sort_key(label, baseline_first=False):
    label = label.replace(data_file_prefix, "")
    m = re.match("([0-9]+)bs_([0-9]+)gpu.*", label)
    if m is not None:
      batch_size, num_gpus = m.groups()
    else:
      batch_size = int(re.match("([0-9]+)bs.*", label).groups()[0])
      num_gpus = 1
    baseline_score = 0.00001 if baseline_first else 100000
    return (int(batch_size) * 10 + int(num_gpus)) *\
      (baseline_score if "baseline" in label else 1)
  data_files.sort(key=lambda d: sort_key(d, plot_baseline_first))

  # Get label
  def get_label(label):
    m = re.match("([0-9]+)bs_([0-9]+)gpu_([0-9]+)vn.*", label)
    if m is not None:
      batch_size, num_gpus, num_vns = re.match("([0-9]+)bs_([0-9]+)gpu_([0-9]+)vn.*", label).groups()
      num_gpus = "%s GPU%s" % (num_gpus, "s" if int(num_gpus) > 1 else "")
    else:
      batch_size, num_vns = re.match("([0-9]+)bs_([0-9]+)vn.*", label).groups()
      num_gpus = ""
    if "2lines" in output_file:
      vns = "no VN" if "baseline" in label else "%s VN" % num_vns
      return "Batch size %s %s (%s)" % (batch_size, num_gpus, vns)
    else:
      # This is for the eval, use VF and don't include batch size
      baseline_name = "TF" if bold_baseline else "TF*"
      system_name = baseline_name if "baseline" in label else "VF"
      if legend_no_batch_size:
        return "%s %s" % (system_name, num_gpus)
      else:
        return "%s %s (BS %s)" % (system_name, num_gpus, batch_size)

  # Plot it
  if figure_size is not None:
    width = float(figure_size.split(",")[0])
    height = float(figure_size.split(",")[1])
    fig = plt.figure(figsize=(width, height))
  else:
    fig = plt.figure()
  ax = fig.add_subplot(1, 1, 1)
  label_font_size = 20 if "resnet-imagenet-V100" in data_files[0] else 24
  ax.set_xlabel(xlabel, fontsize=label_font_size, labelpad=15)
  ax.set_ylabel(ylabel, fontsize=label_font_size, labelpad=15)

  # Figure out colors
  color_cycle = plt.rcParams['axes.prop_cycle'].by_key()['color'] * 10
  if plot_baseline_first:
    num_virtual_experiments = len([d for d in data_files if "baseline" not in d])
    virtual_color_cycle = iter(color_cycle[:num_virtual_experiments] * 10)
    baseline_color_cycle = iter(color_cycle[num_virtual_experiments:] * 10)
  else:
    num_baseline_experiments = len([d for d in data_files if "baseline" in d])
    baseline_color_cycle = iter(color_cycle[:num_baseline_experiments] * 10)
    virtual_color_cycle = iter(color_cycle[num_baseline_experiments:] * 10)

  # Plot the lines
  for data_file in data_files:
    epochs = []
    validation_accuracies = []
    label = data_file.replace(data_file_prefix, "").replace(data_file_suffix, "")
    with open(data_file) as f:
      for i, line in enumerate(f.readlines()):
        if smooth_factor > 0 and i % smooth_factor == 0:
          continue
        split = line.strip().split(" ")
        if len(split) != 2:
          raise ValueError("Expected two columns in data file: %s" % data_file)
        epochs.append(int(split[0]))
        validation_accuracies.append(float(split[1]))
    if steps_per_epoch > 0:
      # The baseline may have more steps per epoch because the batch sizes are smaller
      baseline_steps_multiplier = int(os.getenv("BASELINE_STEPS_MULTIPLIER", 1))\
        if "baseline" in data_file else 1
      x = [steps_per_epoch * baseline_steps_multiplier * e for e in epochs]
    else:
      x = epochs
    y = validation_accuracies
    # Style the lines
    baseline_linestyle = "-" if bold_baseline else "--"
    baseline_linewidth = 6 if bold_baseline else 2
    virtual_linestyle = "--" if bold_baseline else "-"
    virtual_linewidth = 2 if bold_baseline else 4
    virtual_marker = "" if bold_baseline else "x"
    if "baseline" in data_file:
      ax.plot(x, y, label=label, linestyle=baseline_linestyle, linewidth=baseline_linewidth,\
        color=next(baseline_color_cycle))
    else:
      ax.plot(x, y, label=label, linestyle=virtual_linestyle, linewidth=virtual_linewidth,\
        marker=virtual_marker, markeredgewidth=2, color=next(virtual_color_cycle))

  # Legend
  handles, labels = ax.get_legend_handles_labels()
  labels, handles = zip(*sorted(zip(labels, handles),\
    key=lambda pair: sort_key(pair[0], legend_baseline_first)))
  labels = [get_label(l) for l in labels]
  if put_legend_outside:
    box = ax.get_position()
    ax.set_position([box.x0, box.y0, box.width * 0.8, box.height])
    ax.legend(handles, labels, loc='center left', bbox_to_anchor=(1, 0.5),\
      fontsize=legend_font_size, ncol=legend_ncol, columnspacing=1)
  else:
    ax.legend(handles, labels, loc='lower right',
      fontsize=legend_font_size, ncol=legend_ncol, columnspacing=1)

  if space_xticks_apart:
    ax.set_xticks([max(xx, 0) for xx in ax.get_xticks()[::2]])
  if ylim is not None:
    lower = float(ylim.split(",")[0])
    upper = float(ylim.split(",")[1])
    plt.ylim(lower, upper)
  plt.xticks(fontsize=16)
  plt.yticks(fontsize=16)
  plt.title(title, fontsize=label_font_size, pad=20)
  fig.set_tight_layout({"pad": 1.5})
  fig.savefig(output_file, bbox_inches="tight")
  print("Saved to %s" % output_file)

if __name__ == "__main__":
  main()

