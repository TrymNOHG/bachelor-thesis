#!/bin/bash

default_hours=6
default_nodes=1
default_cores=2
default_memory="32G"

usage() {
  echo "Usage for default configurations: $0 <node_type> <hours>"
  echo "Available node types: small, medium, large"
  echo "Usage for custom configuration: $0 <hours> <cores> <memory> <nodes>"
  echo "Using default values if not all parameters are provided for custom configuration."
  exit 1
}

if [ $# -eq 0 ]; then
  # No arguments, use all default values
  hours=$default_hours
  cores=$default_cores
  memory=$default_memory
  nodes=$default_nodes
elif [ $# -eq 1 ]; then
  # Only one argument, assume it's hours and use other defaults
  hours=$1
  cores=$default_cores
  memory=$default_memory
  nodes=$default_nodes
elif [ $# -eq 2 ] || [ $# -eq 3 ]; then
  node_type=$1

  case $node_type in
    small)
      hours=$2
      cores=16
      memory="64G"
	    nodes=$default_nodes
      ;;
    medium)
      hours=$2
      cores=32
      memory="128G"
	    nodes=$default_nodes
      ;;
    large)
      hours=$2
      cores=64
      memory="256G"
	    nodes=$default_nodes
      ;;
    *)
      hours=$1
      cores=${2:-$default_cores}
      memory=${3:-$default_memory}
	    nodes=$default_nodes
      ;;
  esac
elif [ $# -eq 4 ]; then
  hours=$1
  cores=${2:-$default_cores}
  memory=${3:-$default_memory}
  nodes=${4:-$default_nodes}
else
  usage
fi

days=$((hours / 24))
remaining_hours=$((hours % 24))
time_format="$days-$remaining_hours:00:00"

echo "Job submitted: $nodes node(s) created for $hours hour(s) with $cores core(s) and $memory."

salloc --nodes=$nodes --cpus-per-task=$cores --mem=$memory --partition=CPUQ --time=$time_format