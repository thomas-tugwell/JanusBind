import os
import subprocess
import argparse


def make_directory(path):
    os.makedirs(path, exist_ok=True)


def run_ligandmpnn(input_pdb, output_dir, cycle, chains_to_design, seed=111, temperature=2.0):
    mpnn_dir = os.path.join(output_dir, f"mpnn/mpnn_cycle_{cycle}")
    make_directory(mpnn_dir)

    command = (
        f"python run.py --model_type 'soluble_mpnn' --seed {seed} "
        f"--pdb_path {input_pdb} --out_folder {mpnn_dir} "
        f"--number_of_batches 1 --batch_size 1 --pack_side_chains 1 "
        f"--number_of_packs_per_design 1 --homo_oligomer 1 --chains_to_design {chains_to_design} "
        f"--temperature {temperature}"
    )
    print(f"Running LigandMPNN cycle {cycle}...")
    subprocess.run(command, shell=True, check=True)

    # Find the output packed PDB (assuming consistent naming convention)
    for root, _, files in os.walk(os.path.join(mpnn_dir, "packed")):
        for file in files:
            if file.endswith(".pdb"):
                return os.path.join(root, file)
    raise FileNotFoundError("No packed PDB file found after LigandMPNN.")


def run_rosetta_fastrelax(input_pdb, output_dir, cycle, xml_script="symm_design.xml"):
    relax_dir = os.path.join(output_dir, f"relax/relax_cycle_{cycle}")
    make_directory(relax_dir)

    command = (
        f"rosetta_scripts.mpi.linuxgccrelease -parser:protocol {xml_script} "
        f"-s {input_pdb} -out:pdb -out:path:all {relax_dir} -ex1 -ex2aro -nstruct 1"
    )
    print(f"Running Rosetta FastRelax cycle {cycle}...")
    subprocess.run(command, shell=True, check=True)

    for file in os.listdir(relax_dir):
        if file.endswith(".pdb"):
            return os.path.join(relax_dir, file)
    raise FileNotFoundError("No PDB output from Rosetta FastRelax.")


def main():
    parser = argparse.ArgumentParser(description="Iterative LigandMPNN + Rosetta FastRelax driver")
    parser.add_argument("--input_pdb", type=str, required=True, help="Initial input PDB file")
    parser.add_argument("--output_base", type=str, default="./outputs", help="Base output directory")
    parser.add_argument("--job_name", type=str, required=True, help="Name for the output job")
    parser.add_argument("--chains_to_design", type=str, default="A,C,E,G,I", help="Comma-separated list of chains to design")
    parser.add_argument("--num_cycles", type=int, default=3, help="Number of MPNN + Relax cycles")
    parser.add_argument("--temperature", type=float, default=2.0, help="Sampling temperature for MPNN")
    parser.add_argument("--seed", type=int, default=111, help="Random seed")
    args = parser.parse_args()

    job_dir = os.path.join(args.output_base, args.job_name)
    input_pdb = args.input_pdb

    for cycle in range(1, args.num_cycles + 1):
        mpnn_output = run_ligandmpnn(
            input_pdb=input_pdb,
            output_dir=job_dir,
            cycle=cycle,
            chains_to_design=args.chains_to_design,
            seed=args.seed,
            temperature=args.temperature,
        )

        relaxed_output = run_rosetta_fastrelax(
            input_pdb=mpnn_output,
            output_dir=job_dir,
            cycle=cycle,
        )

        input_pdb = relaxed_output  # feed into next cycle

    print("All cycles completed.")


if __name__ == "__main__":
    main()
