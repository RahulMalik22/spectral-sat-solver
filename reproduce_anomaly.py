import ctypes
import numpy as np
import random
import time
import os
import sys

# --- CONFIGURATION ---
LIB_PATH = './sat_core.so'

def load_engine():
    if not os.path.exists(LIB_PATH):
        print(f"Error: {LIB_PATH} not found.")
        print("Run: g++ -shared -o sat_core.so -fPIC sat_core.cpp -O3")
        sys.exit(1)
        
    lib = ctypes.CDLL(LIB_PATH)
    # Define C++ Function Signatures
    lib.walk_sat.argtypes = [
        np.ctypeslib.ndpointer(dtype=np.int32), # clauses (flat)
        ctypes.c_int,                           # num_clauses
        ctypes.c_int,                           # num_vars
        np.ctypeslib.ndpointer(dtype=np.int32), # assignment (output)
        ctypes.c_int                            # max_flips
    ]
    return lib

def generate_phase_transition(n_vars):
    # Ratio 4.26 (The Hardest Region)
    n_clauses = int(n_vars * 4.26)
    clauses = []
    for _ in range(n_clauses):
        vars_idx = random.sample(range(1, n_vars + 1), 3)
        # Random negation
        literals = [v if random.random() > 0.5 else -v for v in vars_idx]
        clauses.extend(literals)
    return np.array(clauses, dtype=np.int32), n_clauses

def run_test(n_vars, max_flips=100_000_000):
    lib = load_engine()
    
    print(f"\n--- BENCHMARK N={n_vars} (Ratio 4.26) ---")
    flat_clauses, n_clauses = generate_phase_transition(n_vars)
    assignment = np.zeros(n_vars + 1, dtype=np.int32)
    
    print(f"Search Space: 2^{n_vars}")
    start_time = time.time()
    
    # CALL C++ ENGINE
    result = lib.walk_sat(flat_clauses, n_clauses, n_vars, assignment, max_flips)
    
    duration = time.time() - start_time
    
    if result == 1:
        print(f"[SUCCESS] Solved in {duration:.4f} seconds.")
        # Verify a few vars
        print(f"Sample Solution: {assignment[1:10]}...")
    else:
        print(f"[TIMEOUT] Could not solve within {max_flips} flips.")

if __name__ == "__main__":
    print(" reproducing 'Inverse Scaling' Anomaly...")
    
    # Test 1: The "Hard" Case
    run_test(n_vars=300)
    
    # Test 2: The "Anomaly" Case (Should be faster)
    run_test(n_vars=500)
