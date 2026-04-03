import argparse
import sys
import dpdata
import ase.io

def parse_args():
    parser = argparse.ArgumentParser(
             description="Usage: python script.py <input_file> <pert_num> <cell_pert_fraction> <atom_pert_distance> <atom_pert_style>")
    parser.add_argument('input_file', help='The path to input structure file (e.g., POSCAR, .cif, .xyz)')
    parser.add_argument('pert_num', type=int, default=20, help='The perturbation number')
    parser.add_argument('cell_pert_fraction', type=float, default=0.03, help='The fraction of cell perturbation')
    parser.add_argument('atom_pert_distance', type=float, default=0.2, help='The distance of atom perturbation')
    parser.add_argument('atom_pert_style', type=str, default='uniform', choices=['normal', 'uniform', 'const'], help='The style for atom perturbation')
    
    parser.add_argument('-f', '--format', type=str, choices=['vasp', 'cp2k'], 
                        help='Output format (vasp or cp2k). If not provided, an interactive menu will appear.')
    return parser.parse_args()

def main():
    try:
        args = parse_args()
    except SystemExit:
        print(f"Default values: pert_num=20, cell_pert_fraction=0.03, atom_pert_distance=0.2, atom_pert_style=uniform")
        sys.exit(1)

    if args.pert_num <= 0:
        print(f"\n[Error] Invalid pert_num: {args.pert_num}. The perturbation number must be a positive integer.")
        sys.exit(1)

    print(f"Reading '{args.input_file}' and performing perturbation...")
    try:
        atoms = ase.io.read(args.input_file)
        system = dpdata.System(atoms, fmt='ase/structure')
    except Exception as e:
        print(f"\n[Error] Failed to read or convert the input file: {e}")
        sys.exit(1)

    perturbed_systems = system.perturb(pert_num=args.pert_num,
                                       cell_pert_fraction=args.cell_pert_fraction,
                                       atom_pert_distance=args.atom_pert_distance,
                                       atom_pert_style=args.atom_pert_style)
    if args.format == 'vasp':
        choice = '1'
    elif args.format == 'cp2k':
        choice = '2'
    else:
        print("\n" + "-"*40)
        print("Please select the output format:")
        print("  1) VASP (Output multiple POSCAR files)")
        print("  2) CP2K (Output single perturb.extxyz file)")
        print("-"*40)
        
        choice = input("Enter your choice (1 or 2): ").strip()

    if choice == '1':
        print(f"\nGenerating {args.pert_num} POSCAR files for VASP...")
        width = len(str(args.pert_num))
        for i in range(args.pert_num):
            output_file = f"POSCAR_{str(i + 1).zfill(width)}.vasp"
            perturbed_systems.sub_system(i).to('vasp/poscar', output_file)
        print("Done! VASP structures generated successfully.")

    elif choice == '2':
        output_filename = "perturb.extxyz"
        print(f"\nConverting to ASE format and saving as {output_filename} for CP2K...")
        ase_atoms_list = [perturbed_systems.sub_system(i).to('ase/structure')[0] for i in range(args.pert_num)]
        ase.io.write(output_filename, ase_atoms_list, format='extxyz')
        print(f"Done! Saved to '{output_filename}'.")
        
        print("\n" + "="*55)
        print("👉 提示: CP2K 数据已准备完毕，请转到 [301) 执行单点] 继续。")
        print("="*55 + "\n")

    else:
        print("\n[Error] Invalid choice. Please run the script again and select 1 or 2.")
        sys.exit(1)

if __name__ == "__main__":
    main()
