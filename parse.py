#!/usr/bin/env python

import datetime
import os

import numpy as np


# Parse step times from the given log file, interpolating missing values if necessary
def parse_step_times(log_file):
  with open(log_file) as f:
    # Parse step numbers and timestamps
    steps, timestamps = [], []
    for line in f.readlines():
      if "Segmentation fault" in line:
        print("Warning: detected segmentation fault in %s. Skipping." % log_file)
        return []
      if not line.startswith("I") or "images/sec" not in line or "total" in line:
        continue
      split = line.split()
      steps.append(int(split[4]))
      timestamp = " ".join(split[:2])
      timestamp = datetime.datetime.strptime(timestamp, "I%m%d %H:%M:%S.%f")
      timestamps.append(timestamp)
    # Interpolate missing values
    step_times = []
    for i in range(1, len(steps)):
      step_delta = steps[i] - steps[i-1]
      timestamp_delta = float((timestamps[i] - timestamps[i - 1]).total_seconds())
      step_times += [timestamp_delta / step_delta] * step_delta
    return step_times

