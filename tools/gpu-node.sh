#!/bin/bash

default_hours=6
default_nodes=1
default_gpus=1
default_gpu_models="a100|v100|p100|h100"
default_mem="64G"

usage() {
  echo "Usage for default configurations: $0 <gpu_type> <hours> <gpus>"
  echo "Available GPU types: shit, mid, good, beast"
  echo "Usage for custom configuration: $0 <hours> <gpus> <gpu_models> <memory> <nodes>"
  echo "Using default values if not all parameters are provided for custom configuration."
  exit 1
}

if [ $# -eq 0 ]; then
  # No arguments, use all default values
  hours=$default_hours
  gpus=$default_gpus
  gpu_models=$default_gpu_models
  mem=$default_mem
  nodes=$default_nodes
elif [ $# -eq 1 ]; then
  # Only one argument, assume it's hours and use other defaults
  hours=$1
  gpus=$default_gpus
  gpu_models=$default_gpu_models
  mem=$default_mem
  nodes=$default_nodes
elif [ $# -eq 3 ]; then
  node_type=$1

  case $node_type in
    shit)
      hours=$2
      gpus=$3
      gpu_models="p100"
      mem="64G"
      nodes=$default_nodes
      ;;
    mid)
      hours=$2
      gpus=$3
      gpu_models="v100"
      mem="128G"
      nodes=$default_nodes
      ;;
    good)
      hours=$2
      gpus=$3
      gpu_models="a100"
      mem="256G"
      nodes=$default_nodes
      ;;
    best)
      hours=$2
      gpus=$3
      gpu_models="h100"
      mem="256G"
      nodes=$default_nodes
      ;;
	any)
      hours=$2
      gpus=$3
      gpu_models=$default_gpus
      mem="128G"
      nodes=$default_nodes
      ;;
    *)
      usage
      ;;
  esac
elif [ $# -eq 4]; then
  hours=$1
  gpus=$2
  gpu_models=$3
  mem=$4
  nodes=$default_nodes
elif [ $# -eq 5 ]; then
  hours=$1
  gpus=$2
  gpu_models=$3
  mem=$4
  nodes=$5
else
  usage
fi

days=$((hours / 24))
remaining_hours=$((hours % 24))
time_format="$days-$remaining_hours:00:00"

echo "Job submitted: $nodes node(s) for $hours hour(s) with $gpus GPU(s) of type(s) $gpu_models, and $mem memory."

salloc --nodes=$nodes --gres=gpu:$gpu_models:$gpus --mem=$mem --partition=GPUQ --time=$time_format
