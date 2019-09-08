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
# Data returned is a list of 2-tuples (num_workers, list of values), except for start_times
# `value_to_parse` can be one of:
#    - throughput,
#    - throughput_per_worker,
#    - step_time
#    - total_time
#    - start_times
def parse_file(log_file, is_benchmark=False, value_to_parse="throughput"):
  # Decide which patterns to parse first
  line_parse_condition = None
  throughput_parse_regex = None
  step_split_index = None
  if is_benchmark:
    line_parse_condition = lambda line: "images/sec" in line and "total" not in line
    throughput_parse_pattern  = ".*images/sec: ([\d\.]*).*"
    step_split_index = 4
  else:
    # Ignore the first step after restart because we're still warming up
    line_parse_condition = lambda line: "examples_per_second" in line and "step = 0" not in line
    throughput_parse_pattern = ".*examples_per_second = ([\d\.]*).*"
    step_split_index = 6

  # Actually parse file
  with open(log_file) as f:
    data = []
    current_num_workers = None
    current_values = []
    start_time = None
    for line in f.readlines():
      if is_benchmark and "tf_logging" not in line:
        continue
      if not is_benchmark and "INFO" in line:
        continue
      if "cluster spec synced" in line:
        if current_num_workers is not None and value_to_parse != "total_time" and len(current_values) > 0:
          data.append((current_num_workers, current_values))
          current_values = []
        # Parse num workers
        cluster_spec_json = re.match(".*(\{.*\}).*", line).groups()[0]
        cluster_spec = json.loads(cluster_spec_json)
        current_num_workers = len(cluster_spec["worker"])
      elif line_parse_condition(line):
        if "throughput" in value_to_parse:
          throughput = float(re.match(throughput_parse_pattern, line).groups()[0])
          if value_to_parse == "throughput_per_worker":
            throughput = throughput / current_num_workers
          current_values.append(throughput)
        elif value_to_parse == "step_time" or\
            value_to_parse == "total_time" or\
            value_to_parse == "start_times":
          split = line.split()
          step = int(split[step_split_index].replace(",", ""))
          timestamp = " ".join(split[:2])
          timestamp = datetime.datetime.strptime(timestamp, "I%m%d %H:%M:%S.%f")
          if value_to_parse == "step_time":
            current_values.append((step, timestamp))
          elif value_to_parse == "total_time":
            current_values.append(timestamp)
          elif value_to_parse == "start_times" and start_time is None:
            start_time = timestamp
      elif "Averaging gradients with horovod" in line:
        if value_to_parse == "start_times":
          timestamp = " ".join(line.split()[:2])
          timestamp = datetime.datetime.strptime(timestamp, "I%m%d %H:%M:%S.%f")
          if start_time is not None:
            current_values.append((timestamp - start_time).total_seconds())
          else:
            current_values.append(0)
    # Ignore first batch
    if value_to_parse == "total_time":
      if len(current_values) > 0:
        return [(current_num_workers, [(current_values[-1] - current_values[1]).total_seconds()])]
      else:
        return [(current_num_workers, [])]
    if current_num_workers is not None:
      data.append((current_num_workers, current_values))
    # Skip current_num_workers == 1 when parsing start times
    if value_to_parse == "start_times":
      if len(data) > 0 and data[0][0] == 1:
        data = data[1:]
    return data

# Reduce the values parsed across all log files in the log dir by num_workers
# Throughputs are summed across workers for the benchmark repo and averaged across workers
# for the models repo, while step times are always averaged across workers
# Return two lists: num_workers and values
def parse_dir(log_dir, value_to_parse="throughput"):
  log_files = []
  if os.listdir(log_dir) == ["1"]:
    log_files = validate_mpi_log_dir(log_dir)
  else:
    log_files = [os.path.join(log_dir, f) for f in os.listdir(log_dir) if f.endswith("out")]
  # Figure out which repo this experiment is from
  is_benchmark = None
  with open(log_files[0]) as f:
    is_benchmark = "tf_cnn_benchmark" in f.read()
  # Parse
  data = {}
  for log_file in log_files:
    if value_to_parse == "start_times" and\
        "rank.0/" not in log_file and\
        "rank.00/" not in log_file:
      continue
    for (num_workers, values) in parse_file(log_file, is_benchmark, value_to_parse):
      if num_workers not in data:
        data[num_workers] = []
      if len(values) > 0:
        data[num_workers].append(np.mean(values))
  print(data)
  # Reduce
  for k, v in data.items():
    new_value = None
    if len(v) > 0:
      if value_to_parse == "throughput":
        new_value = sum(v) if is_benchmark else np.mean(v)
      elif value_to_parse == "step_time" or\
          value_to_parse == "throughput_per_worker" or\
          value_to_parse == "total_time":
        new_value = np.mean(v)
      else:
        new_value = v
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

