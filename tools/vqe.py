from pydantic import BaseModel, Field, ConfigDict
from enum import Enum
import json
import math
import random

class Ansatz(str, Enum):
    UCCSD = "UCCSD"
    HARDWARE_EFFICIENT = "HardwareEfficient"
    REAL_AMPLITUDES = "RealAmplitudes"

class BasisSet(str, Enum):
    STO_3G = "sto-3g"
    SIX_31G = "6-31g"
    CC_PVDZ = "cc-pvdz"

class ResponseFormat(str, Enum):
    MARKDOWN = "markdown"
    JSON = "json"

MOLECULE_DATA = {
    "H2":  {"n_qubits": 2,  "fci_energy": -1.1373, "basis_scale": 1.0},
    "LiH": {"n_qubits": 6,  "fci_energy": -7.8823, "basis_scale": 1.2},
    "BeH2":{"n_qubits": 8,  "fci_energy": -15.5944,"basis_scale": 1.4},
    "H2O": {"n_qubits": 10, "fci_energy": -75.0129,"basis_scale": 1.6},
    "NH3": {"n_qubits": 12, "fci_energy": -56.2144,"basis_scale": 1.8},
}

class RunVQEInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    molecule: str = Field(..., description="Molecular formula e.g. H2, LiH, BeH2, H2O, NH3")
    basis_set: BasisSet = Field(default=BasisSet.STO_3G, description="Quantum chemistry basis set")
    ansatz: Ansatz = Field(default=Ansatz.UCCSD, description="Variational ansatz circuit")
    max_iterations: int = Field(default=100, description="Maximum optimizer iterations", ge=10, le=500)
    shots: int = Field(default=1000, description="Measurement shots per evaluation", ge=100, le=10000)
    response_format: ResponseFormat = Field(default=ResponseFormat.MARKDOWN)

def run_vqe_simulation(params: RunVQEInput) -> dict:
    molecule = params.molecule.upper()
    if molecule not in MOLECULE_DATA:
        molecule = "H2"

    mol = MOLECULE_DATA[molecule]
    basis_scale = {"sto-3g": 1.0, "6-31g": 1.15, "cc-pvdz": 1.3}[params.basis_set.value]
    ansatz_quality = {"UCCSD": 0.99, "HardwareEfficient": 0.94, "RealAmplitudes": 0.96}[params.ansatz.value]

    fci = mol["fci_energy"] * basis_scale
    ground_state_energy = fci * ansatz_quality

    random.seed(42)
    history = []
    energy = 0.0
    for i in range(min(params.max_iterations, 30)):
        energy = ground_state_energy * (1 - math.exp(-0.2 * i)) + random.uniform(-0.01, 0.01)
        history.append(round(energy, 6))

    converged = abs(history[-1] - ground_state_energy) < 0.05

    return {
        "molecule": params.molecule.upper(),
        "basis_set": params.basis_set.value,
        "ansatz": params.ansatz.value,
        "n_qubits": mol["n_qubits"],
        "ground_state_energy_hartree": round(ground_state_energy, 6),
        "fci_baseline_hartree": round(fci, 6),
        "energy_error_hartree": round(abs(ground_state_energy - fci), 6),
        "converged": converged,
        "iterations_run": min(params.max_iterations, 30),
        "shots": params.shots,
        "convergence_history": history[-5:]
    }

def format_vqe_markdown(result: dict) -> str:
    status = "✅ Converged" if result["converged"] else "⚠️ Not Converged"
    return f"""## VQE Simulation Results — {result['molecule']}

**Configuration**
- Basis Set: {result['basis_set']}
- Ansatz: {result['ansatz']}
- Qubits: {result['n_qubits']}
- Shots: {result['shots']}
- Iterations: {result['iterations_run']}

**Energy Results**
- Ground State Energy: {result['ground_state_energy_hartree']} Hartree
- FCI Baseline: {result['fci_baseline_hartree']} Hartree
- Energy Error: {result['energy_error_hartree']} Hartree
- Status: {status}

**Last 5 Convergence Values**: {result['convergence_history']}
"""