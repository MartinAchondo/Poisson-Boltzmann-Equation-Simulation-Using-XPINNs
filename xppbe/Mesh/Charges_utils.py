import os
import numpy as np
from dataclasses import dataclass


@dataclass
class Charges():

    q: float
    x_q: np.ndarray
    r_q: float
    atom_name: str
    res_name: str
    res_num: int
    ion_r_explode: float = 3.5

    @property
    def r_explode(self):
        return self.r_q + self.ion_r_explode


def get_charges_list(pqr_path):
    q, x_q, r_q, atom_name, res_name, res_num = import_charges_from_pqr(pqr_path)
    q_list = list()
    for i in range(len(q)):
        q_list.append(Charges(q=q[i],
                              x_q=x_q[i], 
                              r_q=r_q[i], 
                              atom_name=atom_name[i], 
                              res_name=res_name[i], 
                              res_num=res_num[i]))
    return q_list

def import_charges_from_pqr(pqr_path):
    molecule_file = open(pqr_path, "r")
    molecule_data = molecule_file.read().split("\n")
    atom_count = 0
    for line in molecule_data:
        line = line.split()
        if len(line) == 0 or line[0] != "ATOM":
            continue
        atom_count += 1

    q, x_q, r_q, atom_name, res_name, res_num = (
        np.empty((atom_count,)),
        np.empty((atom_count, 3)),
        np.empty((atom_count,)),
        np.empty((atom_count,), dtype=object),
        np.empty((atom_count,), dtype=object),
        np.empty((atom_count,), dtype=object),
    )
    count = 0
    for line in molecule_data:
        line = line.split()
        if len(line) == 0 or line[0] != "ATOM":
            continue
        q[count] = float(line[8])
        x_q[count, :] = line[5:8]
        r_q[count] = float(line[9])
        atom_name[count] = line[2]
        res_name[count] = line[3]
        res_num[count] = line[4]
        count += 1

    return q, x_q, r_q, atom_name, res_name, res_num

def convert_pqr2xyzr(mesh_pqr_path, mesh_xyzr_path,for_mesh=False):
    
    with open(mesh_pqr_path, "r") as pqr_file:
        pqr_data = pqr_file.read().split("\n")
    
    cont = 0
    with open(mesh_xyzr_path, "w") as xyzr_file:
        for line in pqr_data:
            line = line.split()
            if len(line) == 0 or line[0] != "ATOM":
                continue
            nn = '\n' if cont != 0 else ''
            _,_,_,_,_,x,y,z,_,r = line
            xyzr_file.write(f'{nn}{float(x):9.4f} {float(y):9.4f} {float(z):9.4f} {float(r):9.4f}')
            cont += 1
        
        if for_mesh and cont==1:
            xyzr_file.write(f'\n{float(x):9.4f} {float(y)+0.001:9.4f} {float(z)*1.001:9.4f} {float(r)*0.01:9.4f}')

def convert_pdb2pqr(mesh_pdb_path, mesh_pqr_path, force_field, str_flag=""):

    force_field = force_field.upper()
    if str_flag:
        os.system(f"pdb2pqr {str_flag} --ff={force_field} {mesh_pdb_path} {mesh_pqr_path}")
    else:
         os.system(f"pdb2pqr --ff={force_field} {mesh_pdb_path} {mesh_pqr_path}")

    base_path, _ = os.path.splitext(mesh_pdb_path)
    if os.path.exists(base_path+'.log'):
        os.remove(base_path+'.log')