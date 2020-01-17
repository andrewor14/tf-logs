#!/usr/bin/env python3

import datetime
import os
import re
import sys

import numpy as np

from find_alloc import parse_timestamp, prettify_bytes


BATCH_SIZE = 192
INPUT_DIMENSION = 224
UNKNOWN_DETAILS = "unknown"
ALLOCATION_INPUTS = "inputs"
ALLOCATION_ACTIVATIONS = "activations"
ALLOCATION_OTHER = "other"
ALLOCATION_UNKNOWN = "unknown"

def parse_allocation_events(log_file):
  '''
  Parse all allocation and deallocation events.
  Return a list of 4-tuples (timestamp, is_allocate, num_bytes, allocation_id),
  where is_allocate is True if the event is an allocation, and False otherwise.
  '''
  data = []
  with open(log_file) as f:
    for line in f.readlines():
      # TODO: what is gpu_host_bfc?
      if "llocateRaw" not in line or "gpu_host_bfc" in line:
        continue
      split = line.strip().split(" ")
      timestamp = split[1].strip(":")
      is_allocate = split[4] == "AllocateRaw"
      num_bytes = int(split[6])
      allocation_id = int(split[7])
      data.append((timestamp, is_allocate, num_bytes, allocation_id))
  return data

def parse_allocation_details(log_file):
  '''
  Parse details about all allocations in the given log file.
  Return a map from allocation ID to a list of 2-tuples (kernel, dimensions),
  where kernel is a string and dimensions is a list of integers.
  '''
  allocations = {}
  with open(log_file) as f:
    for line in f.readlines():
      # TODO: what is gpu_host_bfc?
      if "MemoryLog" not in line or "gpu_host_bfc" in line:
        continue
      # Parse allocation details
      allocation_id = re.match(".*allocation_id: ([0-9]*).*", line)
      kernel = re.match(".*kernel_name: \"([^\"]*)\".*", line)
      dimensions = [int(d) for d in re.findall("dim { size: ([0-9]*) }", line)]
      if allocation_id is not None:
        allocation_id = int(allocation_id.groups()[0])
      if kernel is not None:
        kernel = kernel.groups()[0]
      # Record allocation details
      if kernel is not None and len(dimensions) > 0:
        data = (kernel, dimensions)
        if allocation_id not in allocations:
          allocations[allocation_id] = []
        if data not in allocations[allocation_id]:
          allocations[allocation_id].append(data)
  return allocations

def classify_allocation(allocation_details):
  '''
  Classify an allocation into one of "inputs", "activations", "other", and "unknown".
  Argument is a list of (kernel name, dimensions).
  Return a string that represents this allocation's class. 
  '''
  if allocation_details == UNKNOWN_DETAILS:
    return ALLOCATION_UNKNOWN
  for (kernel, dimensions) in allocation_details:
    if np.count_nonzero(np.array(dimensions) == INPUT_DIMENSION) == 2:
      return ALLOCATION_INPUTS
    elif BATCH_SIZE in dimensions:
      return ALLOCATION_ACTIVATIONS
  return ALLOCATION_OTHER

def get_unreleased_allocations(log_file, until_this_timestamp):
  '''
  Return a map of allocations that were not released by the provided timestamp.
  The map is indexed by allocation ID and contains 2-tuples (timestamp, num_bytes).
  '''
  allocation_details = parse_allocation_details(log_file)
  until_this_timestamp = parse_timestamp(until_this_timestamp)
  unreleased_allocations = {}
  for timestamp, is_allocate, num_bytes, allocation_id in parse_allocation_events(log_file):
    if parse_timestamp(timestamp) > until_this_timestamp:
      break
    if is_allocate:
      details = allocation_details[allocation_id] if allocation_id in allocation_details else UNKNOWN_DETAILS
      unreleased_allocations[allocation_id] = (timestamp, num_bytes, details)
    else:
      del unreleased_allocations[allocation_id]
  return unreleased_allocations

def main():
  args = sys.argv
  if len(args) != 3:
    print("Usage: ./unreleased_allocations.py [log_file] [until_this_timestamp]")
    print("  e.g. ./unreleased_allocations.py training.log 14:09:03.208021")
    sys.exit(1)
  unreleased_allocations = get_unreleased_allocations(args[1], args[2])
  # Break down all unreleased allocations by type
  total_bytes = 0
  allocation_breakdown = {}
  for allocation_id in unreleased_allocations.keys():
    timestamp, num_bytes, details = unreleased_allocations[allocation_id]
    allocation_class = classify_allocation(details)
    if allocation_class not in allocation_breakdown:
      allocation_breakdown[allocation_class] = 0
    allocation_breakdown[allocation_class] += num_bytes
    total_bytes += num_bytes
    print(allocation_id, timestamp, num_bytes, details)
  # Print memory allocations
  print("\n----------------------------------------------------")
  print("Total memory occupied: %s" % prettify_bytes(total_bytes))
  for allocation_type in allocation_breakdown.keys():
    num_bytes = prettify_bytes(allocation_breakdown[allocation_type])
    print("  %s: %s" % (allocation_type, num_bytes))
  print("----------------------------------------------------")

if __name__ == "__main__":
  main()

