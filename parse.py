#!/usr/bin/env python

import datetime
import math
import json
import os
import re
import sys

import numpy as np


VERBOSE = False

# Validate the specified MPI log dir and return the log files.
# The structure should be log_dir/1/rank.x, where x+1 is the number of nodes used in the job.
# If we're interested in the horovod trace, then only check that the trace exists and return it.
def validate_mpi_log_dir(log_dir):
  temp_dir = os.listdir(log_dir)
  if "1" not in temp_dir:
    raise ValueError("ERROR: expected structure log_dir/1, was %s" % temp_dir)
  log_dir = os.path.join(log_dir, "1")
  for d in os.listdir(log_dir):
    if not d.startswith("rank"):
      raise ValueError("ERROR: expected structure log_dir/1/rank.x, was %s" % d)
    log_files = os.listdir(os.path.join(log_dir, d))
    if "stderr" not in log_files:
      raise ValueError("ERROR: expected log dir to contain file 'stderr', was %s" % log_files)
  log_files = [os.path.join(os.path.join(log_dir, d), "stderr") for d in os.listdir(log_dir)]
  return log_files

# Parse values from the given log file, indexed by number of workers
# Data returned is a list of 2-tuples (num_workers, list of values)
# `value_to_parse` can be one of "throughput", "throughput_per_worker", or "step_time"
def parse_file(log_file, value_to_parse="throughput"):
  with open(log_file) as f:
    data = []
    current_num_workers = None
    current_values = []
    for line in f.readlines():
      if "tf_logging" not in line:
        continue
      if "cluster spec synced" in line:
        if current_num_workers is not None:
          data.append((current_num_workers, current_values))
          current_values = []
        # Parse num workers
        cluster_spec_json = re.match(".*(\{.*\}).*", line).groups()[0]
        cluster_spec = json.loads(cluster_spec_json)
        current_num_workers = len(cluster_spec["worker"])
      elif "images/sec" in line and "total" not in line:
        if "throughput" in value_to_parse:
          throughput = float(re.match(".*images/sec: ([\d\.]*).*", line).groups()[0])
          current_values.append(throughput)
        elif value_to_parse == "step_time":
          split = line.split()
          step = int(split[4])
          timestamp = " ".join(split[:2])
          timestamp = datetime.datetime.strptime(timestamp, "I%m%d %H:%M:%S.%f")
          current_values.append((step, timestamp))
    if current_num_workers is not None:
      data.append((current_num_workers, current_values))
    # If we're parsing step times, interpolate missing values
    if value_to_parse == "step_time":
      new_data = []
      for (num_workers, values) in data:
        steps, timestamps, step_times = [], [], []
        for (step, timestamp) in values:
          steps.append(step)
          timestamps.append(timestamp)
        for i in range(1, len(steps)):
          step_delta = steps[i] - steps[i-1]
          timestamp_delta = float((timestamps[i] - timestamps[i - 1]).total_seconds())
          step_times += [timestamp_delta / step_delta] * step_delta
        new_data.append((num_workers, step_times))
      data = new_data
    return data

# Reduce the values parsed across all log files in the log dir by num_workers
# Throughputs are summed across workers while step times are averaged across workers
# Return two lists: num_workers and values
def parse_dir(log_dir, value_to_parse="throughput"):
  log_files = [os.path.join(log_dir, f) for f in os.listdir(log_dir) if f.endswith("out")]
  data = {}
  for log_file in log_files:
    for (num_workers, values) in parse_file(log_file, value_to_parse):
      if num_workers not in data:
        data[num_workers] = []
      if len(values) > 0:
        data[num_workers].append(np.mean(values))
  # Reduce
  for k, v in data.items():
    new_value = None
    if len(v) > 0:
      if value_to_parse == "throughput":
        new_value = sum(v)
      elif value_to_parse == "step_time" or value_to_parse == "throughput_per_worker":
        new_value = np.mean(v)
    if new_value is not None:
      data[k] = new_value
    else:
      data[k] = None
  # Split into two lists for ease of plotting
  num_workers, values = [], []
  for k in sorted(data.keys()):
    if data[k] is not None:
      num_workers.append(k)
      values.append(data[k])
  return num_workers, values

