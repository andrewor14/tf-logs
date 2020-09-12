#!/usr/bin/env python3

import datetime
from enum import Enum
import os
import re
import sys

import numpy as np

from find_alloc import find_alloc, parse_timestamp, prettify_bytes


UNKNOWN_DETAILS = "unknown"
READ_VARIABLE_OP = "ReadVariableOp"
ALLOCATE_TEMP = "allocate_temp"
ALLOCATION_TIMESTAMPS = "timestamps"

class AllocationCategories(Enum):
  '''
  Constants that represent all memory allocation categories.
  '''
  INPUTS = "inputs"
  ACTIVATIONS = "activations"
  KERNEL_TEMP = "kernel_temp"
  OTHER = "other"
  PARAMETERS = "parameters"
  UNKNOWN = "unknown"

def should_ignore_line(line):
  '''
  Return true if the given line in a log file should be ignored during parsing.
  '''
  return "gpu_host_bfc" in line or\
    line.startswith("+") or\
    line.startswith("-") or\
    line.startswith(" ") or\
    "null ptr" in line

def parse_allocation_events(log_file):
  '''
  Parse all allocation and deallocation events.
  Return a list of 4-tuples (timestamp, is_allocate, num_bytes, allocation_id),
  where is_allocate is True if the event is an allocation, and False otherwise.
  '''
  data = []
  with open(log_file) as f:
    for i, line in enumerate(f.readlines()):
      if "llocateRaw" not in line or should_ignore_line(line):
        continue
      try:
        split = line.strip().split(" ")
        timestamp = split[1].strip(":")
        from find_alloc import parse_timestamp
        parse_timestamp(timestamp)
        is_allocate = split[-4] == "AllocateRaw"
        num_bytes = int(split[-2])
        allocation_id = int(split[-1])
        data.append((timestamp, is_allocate, num_bytes, allocation_id))
      except Exception as e:
        print("Bad line (%s): %s" % (i, line))
        raise e
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
      if "MemoryLog" not in line or should_ignore_line(line):
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

def classify_allocation(allocation_details, batch_size=None, input_dimension=None):
  '''
  Classify an allocation into one of "inputs", "activations", "other", and "unknown".
  Argument is a list of (kernel name, dimensions).
  Return a string that represents this allocation's class. 
  '''
  # Maybe read batch size and input dimensions from environment variables
  if batch_size is None:
    batch_size = int(os.getenv("BATCH_SIZE") or 192)
  if input_dimension is None:
    input_dimension = int(os.getenv("INPUT_DIMENSION") or 224)
  # Classify allocation
  if allocation_details == UNKNOWN_DETAILS:
    return AllocationCategories.UNKNOWN
  for (kernel, _) in allocation_details:
    if ALLOCATE_TEMP in kernel:
      return AllocationCategories.KERNEL_TEMP
  for (kernel, dimensions) in allocation_details:
    if np.count_nonzero(np.array(dimensions) == input_dimension) == 2:
      return AllocationCategories.INPUTS
    elif batch_size in dimensions:
      return AllocationCategories.ACTIVATIONS
    elif READ_VARIABLE_OP in kernel:
      return AllocationCategories.PARAMETERS
  return AllocationCategories.OTHER

def get_allocations_by_category(log_file):
  '''
  Return a map of bytes allocated over time, indexed by the category of the allocation.

  The returned map has a special 'timestamps' value that is a list of all the timestamps
  that corresponding to allocation changes. All other values have the same length as this
  timestamps list.
  '''
  allocation_details = parse_allocation_details(log_file)
  allocations_by_category = {}
  allocations_by_category[ALLOCATION_TIMESTAMPS] = []
  # Classify each allocation and keep track of bytes allocated across all categories
  for timestamp, is_allocate, num_bytes, alloc_id in parse_allocation_events(log_file):
    details = allocation_details[alloc_id] if alloc_id in allocation_details else UNKNOWN_DETAILS
    category = classify_allocation(details)
    # Append to each list: only the current category gets an updated value
    for cat in AllocationCategories:
      if cat.value not in allocations_by_category:
        allocations_by_category[cat.value] = []
      allocations = allocations_by_category[cat.value]
      new_value = allocations[-1] if len(allocations) > 0 else 0
      if cat == category:
        delta = num_bytes if is_allocate else num_bytes * -1
        new_value += delta
      allocations.append(new_value)
    allocations_by_category[ALLOCATION_TIMESTAMPS].append(timestamp)
  return allocations_by_category

def get_unreleased_allocations(log_file, time_elapsed):
  '''
  Return a map of allocations that were not released at the specified time.
  The map is indexed by allocation ID and contains 3-tuples (timestamp, num_bytes, details).
  '''
  allocation_details = parse_allocation_details(log_file)
  allocation_events = parse_allocation_events(log_file)
  first_timestamp = parse_timestamp(parse_allocation_events(log_file)[0][0])
  unreleased_allocations = {}
  for timestamp, is_allocate, num_bytes, allocation_id in allocation_events:
    if (parse_timestamp(timestamp) - first_timestamp).total_seconds() > time_elapsed:
      break
    if is_allocate:
      details = allocation_details[allocation_id] if allocation_id in allocation_details else UNKNOWN_DETAILS
      unreleased_allocations[allocation_id] = (timestamp, num_bytes, details)
    else:
      if allocation_id in unreleased_allocations:
        del unreleased_allocations[allocation_id]
      else:
        print("Warning: releasing unknown allocation %s" % allocation_id)
  return unreleased_allocations

def main():
  args = sys.argv
  if len(args) != 2 and len(args) != 3:
    print("Usage: ./unreleased_allocations.py [log_file] <[time_elapsed]>")
    print("  e.g. ./unreleased_allocations.py training.log 15")
    sys.exit(1)
  # If no timestamp is given, try to deduce it from the corresponding data file
  log_file = args[1]
  if len(args) == 2:
    time_elapsed, _ = find_alloc(log_file.replace(".log", ".txt"))
  else:
    time_elapsed = float(args[2])
  unreleased_allocations = get_unreleased_allocations(log_file, time_elapsed)
  # Break down all unreleased allocations by type
  num_parameters = 0
  total_bytes = 0
  bytes_by_category = {}
  ids_by_category = {}
  for allocation_id in unreleased_allocations.keys():
    timestamp, num_bytes, details = unreleased_allocations[allocation_id]
    category = classify_allocation(details)
    if category not in bytes_by_category:
      bytes_by_category[category] = 0
      ids_by_category[category] = []
    bytes_by_category[category] += num_bytes
    ids_by_category[category].append(allocation_id)
    total_bytes += num_bytes
    if category == AllocationCategories.PARAMETERS:
      num_parameters += np.prod(details[0][1])
  # Print allocation details in each category
  first_timestamp = parse_timestamp(parse_allocation_events(log_file)[0][0])
  for category, ids in ids_by_category.items():
    print("======================================================================")
    print("Allocation details for category '%s'" % category)
    for alloc_id in ids:
      timestamp, num_bytes, details = unreleased_allocations[alloc_id]
      alloc_time = (parse_timestamp(timestamp) - first_timestamp).total_seconds()
      print("%s, %.3fs, %s (%s), %s" %\
        (alloc_id, alloc_time, num_bytes, prettify_bytes(num_bytes), details))
    print("======================================================================\n")
  # Print summary stats
  print("----------------------------------------------------")
  print("Memory breakdown at %.3fs:" % time_elapsed)
  print("Num parameters = %s" % num_parameters)
  print("Total memory occupied: %s" % prettify_bytes(total_bytes))
  for category in bytes_by_category.keys():
    num_bytes = prettify_bytes(bytes_by_category[category])
    print("  %s: %s" % (category.value, num_bytes))
  print("----------------------------------------------------")

if __name__ == "__main__":
  main()

