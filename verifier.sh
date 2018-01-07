#!/bin/bash
while IFS='' read -r line || [[ -n "$line" ]]; do
    echo -n "$line" " -> " && echo -n "$line" | md5sum
done
