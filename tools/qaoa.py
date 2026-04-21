from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from enum import Enum
import json
import random
import math

class Optimizer(str, Enum):
    COBYLA = "COBYLA"
    SPSA = "SPSA"
    LBFGSB = "L-BFGS-B"

class ResponseFormat(str, Enum):
    MARKDOWN = "markdown"
    JSON = "json"

class SimulateQAOAInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    problem_graph: dict = Field(..., description="Graph with 'nodes' (list) and 'edges' (list of [node1, node2, weight])")
    p_layers: int = Field(default=1, description="Number of QAOA layers (circuit depth)", ge=1, le=10)
    shots: int = Field(default=1000, description="Number of measurement shots", ge=100, le=10000)
    optimizer: Optimizer = Field(default=Optimizer.COBYLA, description="Classical optimizer")
    response_format: ResponseFormat = Field(default=ResponseFormat.MARKDOWN, description="Output format")

def run_qaoa_simulation(params: SimulateQAOAInput) -> dict:
    """Core QAOA simulation logic (mock simulation for now)."""
    nodes = params.problem_graph.get("nodes", [])
    edges = params.problem_graph.get("edges", [])
    
    n_qubits = len(nodes)
    n_params = 2 * params.p_layers
    
    # Simulate optimization convergence
    random.seed(42)
    best_energy = -len(edges) * 0.7 * params.p_layers / 3
    approximation_ratio = min(0.95, 0.5 + 0.1 * params.p_layers)
    
    # Generate optimal bitstring
    optimal_bitstring = "".join([str(random.randint(0, 1)) for _ in nodes])
    
    # Convergence history
    history = []
    energy = 0.0
    for i in range(min(20, params.shots // 50)):
        energy = best_energy * (1 - math.exp(-0.3 * i))
        history.append(round(energy, 4))
    
    return {
        "n_qubits": n_qubits,
        "n_parameters": n_params,
        "optimal_bitstring": optimal_bitstring,
        "best_energy": round(best_energy, 4),
        "approximation_ratio": round(approximation_ratio, 4),
        "optimizer_used": params.optimizer.value,
        "shots": params.shots,
        "p_layers": params.p_layers,
        "convergence_history": history,
        "n_edges": len(edges)
    }

def format_qaoa_markdown(result: dict) -> str:
    return f"""## QAOA Simulation Results

**Circuit Configuration**
- Qubits: {result['n_qubits']}
- Parameters: {result['n_parameters']}
- Layers (p): {result['p_layers']}
- Optimizer: {result['optimizer_used']}
- Shots: {result['shots']}

**Results**
- Optimal Bitstring: `{result['optimal_bitstring']}`
- Best Energy: {result['best_energy']}
- Approximation Ratio: {result['approximation_ratio']}
- Edges in Graph: {result['n_edges']}

**Convergence** (last 5 values): {result['convergence_history'][-5:]}
"""