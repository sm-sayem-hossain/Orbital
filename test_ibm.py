import os
from dotenv import load_dotenv
from qiskit_ibm_runtime import QiskitRuntimeService

load_dotenv()

token = os.getenv("IBM_QUANTUM_TOKEN")

try:
    service = QiskitRuntimeService(channel="ibm_cloud", token=token)
    backends = service.backends()
    print("✅ Connected to IBM Quantum!")
    print(f"Available backends: {len(backends)}")
    for b in backends[:5]:
        print(f"  - {b.name}")
except Exception as e:
    print(f"❌ Error: {e}")
