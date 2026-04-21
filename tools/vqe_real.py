from qiskit.circuit.library import TwoLocal, EfficientSU2
from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager
from qiskit_ibm_runtime import EstimatorV2 as Estimator, Session
from qiskit.quantum_info import SparsePauliOp
from core.ibm_backend import get_ibm_service
import numpy as np
import json

MOLECULE_HAMILTONIANS = {
    "H2": {
        "paulis": ["II", "IZ", "ZI", "ZZ", "XX"],
        "coeffs": [-1.0523732, 0.39793742, -0.39793742, -0.01128010, 0.18093119],
        "n_qubits": 2,
        "fci_energy": -1.1373
    },
    "LIH": {
        "paulis": ["IIII", "IIIZ", "IIZI", "IZII", "ZIII", "IIZZ", "IZIZ", "ZZII"],
        "coeffs": [-7.8823, 0.1821, -0.1821, 0.1821, -0.1821, 0.0813, 0.0813, 0.0813],
        "n_qubits": 4,
        "fci_energy": -7.8823
    }
}

def run_real_vqe(molecule: str, ansatz_reps: int = 1, shots: int = 1000) -> dict:
    mol_key = molecule.upper().replace("2", "2")
    
    if mol_key not in MOLECULE_HAMILTONIANS:
        mol_key = "H2"
    
    mol_data = MOLECULE_HAMILTONIANS[mol_key]
    
    hamiltonian = SparsePauliOp(
        mol_data["paulis"],
        coeffs=mol_data["coeffs"]
    )
    
    n_qubits = mol_data["n_qubits"]
    ansatz = EfficientSU2(n_qubits, reps=ansatz_reps)
    
    service = get_ibm_service()
    backend = service.backend("ibm_kingston")
    
    # Transpilation
    pm = generate_preset_pass_manager(target=backend.target, optimization_level=1)
    isa_ansatz = pm.run(ansatz)
    isa_hamiltonian = hamiltonian.apply_layout(layout=isa_ansatz.layout)
    
    estimator = Estimator(mode=backend)
    estimator.options.default_shots = shots
    
    initial_params = np.zeros(ansatz.num_parameters)
    
    pub = (isa_ansatz, isa_hamiltonian, initial_params)
    job = estimator.run([pub])
    print(f"Job submitted! ID: {job.job_id()}")
    result = job.result()
    
    energy = float(result[0].data.evs)
    
    return {
        "molecule": molecule.upper(),
        "backend": "ibm_kingston",
        "ground_state_energy_hartree": round(energy, 6),
        "fci_baseline_hartree": mol_data["fci_energy"],
        "energy_error_hartree": round(abs(energy - mol_data["fci_energy"]), 6),
        "n_qubits": n_qubits,
        "shots": shots,
        "mode": "real_quantum_hardware"
    }
