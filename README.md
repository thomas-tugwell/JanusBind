# JanusBind
<img width="863" alt="image" src="https://github.com/user-attachments/assets/c7fb8694-2640-45ba-a66a-628478e85f25" />

# Installation:

JanusBind was built with Python 3.11 and requires PyRosetta, therefore it is recommended you compile [this](https://graylab.jhu.edu/download/PyRosetta4/archive/release/PyRosetta4.Debug.python311.linux/PyRosetta4.Debug.python311.linux.release-387.tar.bz2) version of PyRosetta from source. Testing was not performed on any other versions.

JanusBind uses the LigandMPNN repo for binder sequence generation and pre-packing. Clone the repo into the main directory of JanusBind with
```git clone https://github.com/dauparas/LigandMPNN.git```



#Example Run
```
python symm_mpnn_relax.py --input_pdb ./C5_3_9_dn10_AB_trunc_input_0001_renum.pdb --symmdef ./C5.symm --output_base testing_cycles --job_name cycles_job --num_cycles 3
```
