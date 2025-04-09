#!/usr/bin/env bash

# Check that exactly two arguments are provided: input pdb and output pdb.
if [ "$#" -ne 2 ]; then
  echo "Usage: $0 input.pdb output.pdb"
  exit 1
fi

input_file="$1"
output_file="$2"

# Extract chains A, B, C, D, E from the input file and renumber them.
pdb_selchain -A "$input_file" | pdb_reres -1 > chain_A.pdb
pdb_selchain -B "$input_file" | pdb_reres -1 > chain_B.pdb
pdb_selchain -C "$input_file" | pdb_reres -1 > chain_C.pdb
pdb_selchain -D "$input_file" | pdb_reres -1 > chain_D.pdb
pdb_selchain -E "$input_file" | pdb_reres -1 > chain_E.pdb
pdb_selchain -F "$input_file" | pdb_reres -1 > chain_F.pdb
pdb_selchain -G "$input_file" | pdb_reres -1 > chain_G.pdb
pdb_selchain -H "$input_file" | pdb_reres -1 > chain_H.pdb
pdb_selchain -I "$input_file" | pdb_reres -1 > chain_I.pdb
pdb_selchain -J "$input_file" | pdb_reres -1 > chain_J.pdb

# Concatenate all extracted chains into the output file.
cat chain_*.pdb > "$output_file"

# Delete the intermediate chain files.
rm chain_A.pdb chain_B.pdb chain_C.pdb chain_D.pdb chain_E.pdb chain_F.pdb chain_G.pdb chain_H.pdb chain_I.pdb chain_J.pdb

echo "Created $output_file from $input_file."

