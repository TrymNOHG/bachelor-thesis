#!/bin/bash

if [ $# -eq 0 ]; then
	echo "No path entered."
	exit 1
fi

slurm_path=$1
echo "Attempting to find slurm"

if [ ! -f "$slurm_path" ]; then
	echo "$slurm_path not found"
	exit 1
fi


file_path=$2
echo "Attempting run job on file: $file_path"

echo "Checking if file exists"

if [ ! -f "$file_path" ]; then
	echo "$file_path could not be found."
	exit 1
fi

extension="${file_path##*.}"

if [ "$extension" = "ipynb" ]; then
	echo "The file has a .ipynb extension."
	new_file_name="jupyter_to_python"
	jupyter nbconvert --to python $file_path --output $new_file_name
	directory=$(dirname "$path")
	file_path="$directory/$new_file_name.py"
elif [ "$extension" = "py" ]; then
    echo "The file has a .py extension."
else
    echo "The file has a different extension."
    exit 1
fi

echo "$file_path was found. Starting job"
sbatch "$slurm_path" "$file_path"
