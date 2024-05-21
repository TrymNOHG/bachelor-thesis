#!/bin/bash

if [ $# -ne 2 ] && [ $# -ne 3 ]; then
  echo "There are two ways to use this script:"
  echo "With defined port: $0 <node> <username> <local_port>"
  echo "With default port: $0 <node> <username> (default port is 6000)"
  exit 1
fi

default_port=6000

node=$1
username=$2
local_port=${3:-default_port}

echo "Attempting to establish an SSH tunnel..."
ssh -L $local_port:$node:22 $username@idun-login2.hpc.ntnu.no -N -T &
SSH_PID=$!

sleep 3

if ! ps -p $SSH_PID > /dev/null; then
    echo "SSH tunnel setup failed."
    exit 1
fi

function is_port_open {
    netstat -tnl | grep -q ":$local_port"
    return $?
}

for i in {1..30}; do
    if is_port_open; then
        echo "SSH tunnel established. You can now connect to $node via 'ssh -p $local_port username@localhost'."
        break
    fi
    sleep 1
done

if ! is_port_open; then
    echo "Failed to establish the tunnel."
    kill $SSH_PID
    exit 1
fi

read -p "Press [Enter] to close the tunnel..."

kill $SSH_PID
echo "SSH tunnel closed."
