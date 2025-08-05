#!/bin/bash

# Parallel lists (all the same length)
OCCUPANCY=(
  "Break rooms (General)"
  "Lobbies"
  "Lobbies"
  "Office space"
  "Office space"
  "Office space"
  "Office space"
  "Break rooms (General)"
  "Conference/meeting"
)

AREA=(472 878 205 78 209 204 207 102 231)
PEOPLE=(12 29 7 1 2 2 2 3 12)

# Optional: add a single Recirc_CFM value or list if you want them to vary
RECIRC_CFM=50

# Number of scenarios (should match all list lengths)
N=${#OCCUPANCY[@]}

for ((i=0; i<N; i++)); do
  echo "Running: ${OCCUPANCY[i]}, area ${AREA[i]} ft2, ${PEOPLE[i]} people"
  python3 mainIAQPconsole.py -occupancy "${OCCUPANCY[i]}" -area_ft2 "${AREA[i]}" -num_people "${PEOPLE[i]}" -Recirc_CFM ${RECIRC_CFM}
done
