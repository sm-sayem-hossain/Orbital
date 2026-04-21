import os
from dotenv import load_dotenv
from qiskit_ibm_runtime import QiskitRuntimeService

load_dotenv()

_service = None

def get_ibm_service():
    global _service
    if _service is None:
        token = os.getenv("IBM_QUANTUM_TOKEN")
        if not token:
            raise ValueError("IBM_QUANTUM_TOKEN not found in .env file")
        _service = QiskitRuntimeService(
            channel="ibm_cloud",
            token=token
        )
    return _service

def get_least_busy_backend(min_qubits: int = 2):
    service = get_ibm_service()
    backends = service.backends()
    operational = [b for b in backends if b.num_qubits >= min_qubits]
    if not operational:
        raise ValueError(f"No backends available with {min_qubits}+ qubits")
    return min(operational, key=lambda b: b.num_qubits)

def get_simulator_backend():
    service = get_ibm_service()
    return service.backend("ibm_kingston")
