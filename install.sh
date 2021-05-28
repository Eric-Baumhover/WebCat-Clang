#!/bin/bash

# Check if sudo.
if [ "$EUID" -ne 0 ]
  then echo "Please run as root"
  exit
fi

git clone "https://github.com/CxxTest/cxxtest.git"
chmod -R 777 cxxtest

# Ensure executables are executable.
chmod +x cxxtest/bin/cxxtestgen
chmod +x bin/no-loops
chmod +x bin/no-indexing

# Install dependencies.
apt install -y clang-8
apt install -y llvm-8
apt install -y gcc-5-base
apt install -y gcc-6-base
apt install -y gcc-multilib
