from fastmcp import FastMCP
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from enum import Enum
import json
from tools.qaoa import SimulateQAOAInput, run_qaoa_simulation, format_qaoa_markdown
from tools.vqe import RunVQEInput, run_vqe_simulation, format_vqe_markdown

mcp = FastMCP("qc_simulation_mcp")

class HardwareProfile(str, Enum):
    IDEAL_SIMULATOR = "ideal_simulator"
    NOISY_SIMULATOR = "noisy_simulator"
    IBM_EAGLE = "ibm_eagle"
    IONQ_ARIA = "ionq_aria"

class Algorithm(str, Enum):
    QAOA = "QAOA"
    VQE = "VQE"
    QSVM = "QSVM"
    GROVER = "Grover"

class EstimateResourcesInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    algorithm: Algorithm = Field(..., description="Quantum algorithm to estimate resources for")
    problem_size: int = Field(..., description="Number of qubits/variables required", ge=1, le=100)
    hardware_profile: HardwareProfile = Field(..., description="Target hardware profile")
    include_error_mitigation: bool = Field(default=False, description="Include error mitigation overhead")

@mcp.tool(
    name="qc_estimate_resources",
    annotations={
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False
    }
)
async def qc_estimate_resources(params: EstimateResourcesInput) -> str:
    """Estimate quantum resources needed to run an algorithm without executing it.
    
    Returns qubit count, circuit depth, estimated runtime, and feasibility verdict.
    """
    overhead = 1.5 if params.include_error_mitigation else 1.0

    profiles = {
        HardwareProfile.IDEAL_SIMULATOR: {"max_qubits": 30, "error_rate": 0.0},
        HardwareProfile.NOISY_SIMULATOR: {"max_qubits": 30, "error_rate": 0.01},
        HardwareProfile.IBM_EAGLE: {"max_qubits": 127, "error_rate": 0.001},
        HardwareProfile.IONQ_ARIA: {"max_qubits": 25, "error_rate": 0.0003},
    }

    algo_factors = {
        Algorithm.QAOA: {"depth_factor": 4, "runtime_ms": 200},
        Algorithm.VQE: {"depth_factor": 6, "runtime_ms": 500},
        Algorithm.QSVM: {"depth_factor": 3, "runtime_ms": 150},
        Algorithm.GROVER: {"depth_factor": 5, "runtime_ms": 300},
    }

    hw = profiles[params.hardware_profile]
    af = algo_factors[params.algorithm]

    qubit_count = params.problem_size
    circuit_depth = int(params.problem_size * af["depth_factor"] * overhead)
    runtime_ms = int(af["runtime_ms"] * params.problem_size * overhead)
    fidelity = max(0.0, 1.0 - hw["error_rate"] * circuit_depth)
    feasible = qubit_count <= hw["max_qubits"]

    result = {
        "algorithm": params.algorithm.value,
        "hardware_profile": params.hardware_profile.value,
        "qubit_count": qubit_count,
        "circuit_depth": circuit_depth,
        "estimated_runtime_ms": runtime_ms,
        "fidelity_estimate": round(fidelity, 4),
        "feasibility": "FEASIBLE" if feasible else "NOT FEASIBLE",
        "reason": f"Requires {qubit_count} qubits, hardware supports max {hw['max_qubits']}"
    }

    return json.dumps(result, indent=2)

@mcp.tool(
    name="qc_simulate_qaoa",
    annotations={
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": False,
        "openWorldHint": False
    }
)
async def qc_simulate_qaoa(params: SimulateQAOAInput) -> str:
    """Run a Quantum Approximate Optimization Algorithm simulation on a problem graph.
    
    Solves combinatorial optimization problems like Max-Cut using QAOA.
    Returns optimal bitstring, approximation ratio, and convergence history.
    """
    result = run_qaoa_simulation(params)
    
    if params.response_format.value == "json":
        return json.dumps(result, indent=2)
    else:
        return format_qaoa_markdown(result)

@mcp.tool(
    name="qc_run_vqe",
    annotations={
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": False,
        "openWorldHint": False
    }
)
async def qc_run_vqe(params: RunVQEInput) -> str:
    """Run Variational Quantum Eigensolver to find molecular ground-state energy.
    
    Supports molecules: H2, LiH, BeH2, H2O, NH3.
    Returns ground-state energy in Hartree, convergence history, and FCI baseline comparison.
    """
    result = run_vqe_simulation(params)
    
    if params.response_format.value == "json":
        return json.dumps(result, indent=2)
    else:
        return format_vqe_markdown(result)

if __name__ == "__main__":
    mcp.run()