#!/bin/sh

case "$CONDA_PREFIX" in
  */imglyb-dev)
    ;;
  *)
    echo "Please run 'make setup' and then 'mamba activate imglyb-dev' first."
    exit 1
    ;;
esac
