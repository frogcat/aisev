#!/bin/bash

target_file=/usr/local/lib/python3.12/site-packages/inspect_ai/model/_openai.py

# Add import os to line 6
sed -i '6iimport os' "$target_file"

# Add 3 tabs + proxy=os.environ.get(“http_proxy”) at line 694
sed -i '694i\\t\t\tproxy=os.environ.get("http_proxy")' "$target_file"