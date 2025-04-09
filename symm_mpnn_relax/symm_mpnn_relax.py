import os
import argparse
import subprocess
import shutil
from Bio.PDB import PDBParser, PDBIO, Select

def run_ligandmpnn(input_pdb, output_dir, seed, cycle):
    mpnn_output_dir = os.path.join(output_dir, f"mpnn/mpnn_results_{cycle}")
    os.makedirs(mpnn_output_dir, exist_ok=True)

    cmd = (
        f"python run.py --model_type 'soluble_mpnn' --seed {seed} "
        f"--pdb_path {input_pdb} --out_folder {mpnn_output_dir} "
        f"--number_of_batches 1 --batch_size 1 --pack_side_chains 1 "
        f"--number_of_packs_per_design 1 --homo_oligomer 1 "
        f"--chains_to_design 'A,C,E,G,I' --temperature 2.0"
    )
    print(f"Running LigandMPNN: {cmd}")
    subprocess.run(cmd, shell=True, check=True)

    return os.path.join(mpnn_output_dir, "packed"), mpnn_output_dir

def run_fastrelax(input_pdb, symmdef, output_dir, cycle):
    relax_dir = os.path.join(output_dir, f"relax/relax_cycle_{cycle}")
    os.makedirs(relax_dir, exist_ok=True)

    cmd = (
        f"rosetta_scripts.mpi.linuxgccrelease -parser:protocol symm_design.xml "
        f"-s {input_pdb} -symmetry:symmetry_definition {symmdef} -out:pdb "
        f"-out:path:all {relax_dir} -ex1 -ex2aro -nstruct 1"
    )
    print(f"Running FastRelax: {cmd}")
    subprocess.run(cmd, shell=True, check=True)

    return relax_dir

class ChainSelect(Select):
    def __init__(self, chains_to_keep):
        self.chains_to_keep = chains_to_keep

    def accept_chain(self, chain):
        return chain.id in self.chains_to_keep

def prune_pdb_to_chains(input_pdb_path, output_pdb_path, chains_to_keep=["A", "B"]):
    parser = PDBParser(QUIET=True)
    structure = parser.get_structure("structure", input_pdb_path)

    io = PDBIO()
    io.set_structure(structure)
    io.save(output_pdb_path, ChainSelect(chains_to_keep))
    return output_pdb_path

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input_pdb", required=True, help="Initial input PDB file")
    parser.add_argument("--symmdef", required=True, help="Path to symmetry definition file")
    parser.add_argument("--output_base", default="./outputs", help="Base directory for outputs")
    parser.add_argument("--job_name", required=True, help="Name of the design job")
    parser.add_argument("--seed", type=int, default=111, help="Random seed")
    parser.add_argument("--num_cycles", type=int, default=3, help="Number of design cycles")
    args = parser.parse_args()

    job_dir = os.path.join(args.output_base, args.job_name)
    os.makedirs(job_dir, exist_ok=True)

    input_pdb = args.input_pdb

    for cycle in range(1, args.num_cycles + 1):
        print(f"\n=== Starting Cycle {cycle} ===")

        # Run LigandMPNN
        packed_dir, mpnn_out = run_ligandmpnn(input_pdb, job_dir, args.seed, cycle)

        # Get the output pdb from MPNN (assumes one pdb output)
        mpnn_pdbs = [f for f in os.listdir(packed_dir) if f.endswith(".pdb")]
        if not mpnn_pdbs:
            raise FileNotFoundError("No PDB file found in LigandMPNN packed output.")

        mpnn_pdb_path = os.path.join(packed_dir, mpnn_pdbs[0])
        pruned_pdb_path = os.path.join(job_dir, f"pruned_cycle_{cycle}.pdb")

        # Prune to chains A and B for FastRelax
        prune_pdb_to_chains(mpnn_pdb_path, pruned_pdb_path, ["A", "B"])

        # Run FastRelax
        relax_dir = run_fastrelax(pruned_pdb_path, args.symmdef, job_dir, cycle)

        # Use the output of FastRelax as the next input
        relaxed_pdbs = [f for f in os.listdir(relax_dir) if f.endswith(".pdb")]
        if not relaxed_pdbs:
            raise FileNotFoundError("No PDB file found in FastRelax output.")

        input_pdb = os.path.join(relax_dir, relaxed_pdbs[0])

if __name__ == "__main__":
    main()

