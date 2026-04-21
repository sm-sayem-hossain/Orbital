# Orbital 🔮
### Quantum Simulation MCP Server for AI Agents

Orbital is an open-source MCP (Model Context Protocol) server that gives AI agents native access to quantum computing simulations — enabling drug discovery, molecular energy calculations, and combinatorial optimization directly from natural language.

Built with FastMCP and Python. Works with Gemini CLI, Claude Desktop, and any MCP-compatible AI client.

![Python](https://img.shields.io/badge/Python-3.12-blue?style=flat-square&logo=python)
![FastMCP](https://img.shields.io/badge/FastMCP-3.2.4-purple?style=flat-square)
![MCP](https://img.shields.io/badge/MCP-1.27.0-green?style=flat-square)
![License](https://img.shields.io/badge/License-MIT-yellow?style=flat-square)
![Status](https://img.shields.io/badge/Status-Active-brightgreen?style=flat-square)

## What is Orbital?

Most AI assistants can *talk about* quantum computing. Orbital lets them *do* quantum computing.

When an AI agent connects to Orbital, it gains three powerful quantum tools it can invoke autonomously — no quantum expertise required from the user.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        USER                                 │
│              "Calculate H2 ground state energy"             │
└──────────────────────────┬──────────────────────────────────┘
                           │  Natural Language
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                    AI AGENT                                 │
│                 Gemini CLI / Claude                         │
└──────────────────────────┬──────────────────────────────────┘
                           │  MCP Protocol
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                  ORBITAL SERVER                             │
│                                                             │
│   ┌─────────────────┐  ┌─────────────────┐  ┌──────────┐   │
│   │ qc_estimate_    │  │ qc_simulate_    │  │ qc_run_  │   │
│   │ resources       │  │ qaoa            │  │ vqe      │   │
│   └─────────────────┘  └─────────────────┘  └──────────┘   │
│                                                             │
│              FastMCP 3.2.4  +  Pydantic v2                  │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│              QUANTUM SIMULATION ENGINE                      │
│         Resource Estimation · QAOA · VQE                    │
└─────────────────────────────────────────────────────────────┘
```

## Tools

### `qc_estimate_resources`
Estimates the quantum resources required to run an algorithm **before** executing it. Returns qubit count, circuit depth, runtime estimate, fidelity, and a `FEASIBLE / NOT FEASIBLE` verdict.

| Input | Type | Description |
|-------|------|-------------|
| `algorithm` | enum | QAOA, VQE, QSVM, Grover |
| `problem_size` | int (1–100) | Number of qubits required |
| `hardware_profile` | enum | ideal_simulator, noisy_simulator, ibm_eagle, ionq_aria |
| `include_error_mitigation` | bool | Factor in error mitigation overhead |

> **Example:** *"Can my 20-qubit VQE problem run on IonQ Aria hardware?"*

### `qc_simulate_qaoa`
Runs a Quantum Approximate Optimization Algorithm simulation on a problem graph. Solves Max-Cut and combinatorial optimization problems. Returns optimal bitstring, approximation ratio, and convergence history.

| Input | Type | Description |
|-------|------|-------------|
| `problem_graph` | dict | Nodes and weighted edges as JSON |
| `p_layers` | int (1–10) | Circuit depth |
| `shots` | int (100–10000) | Measurement shots |
| `optimizer` | enum | COBYLA, SPSA, L-BFGS-B |
| `response_format` | enum | markdown or json |

> **Example:** *"Optimize this 6-node supply chain graph using QAOA with 3 layers"*

### `qc_run_vqe`
Runs the Variational Quantum Eigensolver to calculate molecular ground-state energy. Used in quantum chemistry and drug discovery pipelines. Returns energy in Hartree, convergence history, and comparison against FCI baseline.

**Supported molecules:** `H2` · `LiH` · `BeH2` · `H2O` · `NH3`

| Input | Type | Description |
|-------|------|-------------|
| `molecule` | string | Molecular formula |
| `basis_set` | enum | sto-3g, 6-31g, cc-pvdz |
| `ansatz` | enum | UCCSD, HardwareEfficient, RealAmplitudes |
| `max_iterations` | int (10–500) | Optimizer iterations |
| `shots` | int (100–10000) | Measurement shots |

> **Example:** *"Calculate the ground state energy of LiH using the 6-31g basis set"*

## Quickstart

**1. Clone the repository**
```bash
git clone https://github.com/sm-sayem-hossain/Orbital.git
cd Orbital
```

**2. Create virtual environment**
```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS / Linux
source .venv/bin/activate
```

**3. Install dependencies**
```bash
pip install fastmcp
```

**4. Verify setup**
```bash
fastmcp inspect server.py
```

**5. Connect to Gemini CLI**
```bash
gemini mcp add orbital .venv\Scripts\python.exe server.py
gemini
```

**6. Try it**
```
Calculate the ground state energy of H2 molecule using VQE
```

## Project Structure

```
Orbital/
├── server.py              # FastMCP server — main entry point
├── tools/
│   ├── __init__.py
│   ├── qaoa.py            # QAOA simulation logic
│   └── vqe.py             # VQE simulation logic
├── core/                  # Shared utilities (coming soon)
├── models/                # Pydantic models (coming soon)
├── tests/                 # Test suite (coming soon)
├── evals/                 # Agent evaluation Q&A pairs (coming soon)
├── .gitignore
└── README.md
```

## Roadmap

**Phase 1 — Foundation** ✅ `complete`
Working MCP server with 3 quantum tools, Gemini CLI integration, MCP Inspector verified.

**Phase 2 — Real Backends** `next`
Replace mock simulations with real Qiskit and PennyLane backends. Connect to IBM Quantum and IonQ hardware APIs.

**Phase 3 — Expansion** `planned`
Add more algorithms (Grover search, QSVM, QPE), support more molecules, add noise modeling.

**Phase 4 — Production** `planned`
HTTP transport, authentication, rate limiting, cloud deployment.

## Tech Stack

| Component | Technology |
|-----------|------------|
| Language | Python 3.12 |
| MCP Framework | FastMCP 3.2.4 |
| Protocol | MCP 1.27.0 |
| Validation | Pydantic v2 |
| Transport | stdio (local), HTTP (planned) |
| AI Clients | Gemini CLI, Claude Desktop |

## License

MIT License — free to use, modify, and distribute.

## Author

**Sayem Hossain**
Built from scratch as a demonstration of MCP server development for quantum computing applications.
