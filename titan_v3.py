import random
import time
import itertools
import multiprocessing
import os

# --- 1. THE TITAN GENERATOR ---
def generate_titan(n=52):
    print(f"--- INITIALIZING TITAN (Size: {n}) ---")
    half = n // 2
    # Generate large range numbers to ensure complexity
    part_a = [random.randint(-1000000, 1000000) for _ in range(half)]
    sum_a = sum(part_a)
    
    part_b = [random.randint(-1000000, 1000000) for _ in range(half - 1)]
    final_num = -(sum_a + sum(part_b)) 
    part_b.append(final_num)
    
    full_set = part_a + part_b
    random.shuffle(full_set)
    
    print(f"Complexity: 2^{n} ({2**n:,} possibilities).")
    return full_set

# --- 2. WORKER DRONE (The Hydra) ---
def worker_probe(args):
    """
    Parallel worker that scans a specific subset size of the Right Tranche.
    Filters results using the Min/Max Sieve before returning.
    """
    r, right_numbers, min_val, max_val = args
    candidates = []
    
    for subset in itertools.combinations(right_numbers, r):
        s_right = sum(subset)
        target = -s_right
        
        # THE SIEVE: Range Pruning
        if min_val <= target <= max_val:
            candidates.append((target, subset))
            
    return candidates

# --- 3. THE ARCHITECT (Parallel Meet-in-the-Middle) ---
def solve_titan(numbers):
    start_time = time.time()
    
    # SPLIT (Divide and Conquer)
    mid = len(numbers) // 2
    left_tranche = numbers[:mid]
    right_tranche = numbers[mid:]
    
    print(f"[Architect] Splitting Infinite: {len(left_tranche)} Left | {len(right_tranche)} Right")
    
    # PHASE A: PRE-BOIL LEFT (The Vault)
    print(f"[Phase A] Pre-boiling Left Tranche (Building the Anchor)...")
    vault = {}
    
    # Generate all sums for Left Tranche
    for r in range(1, len(left_tranche) + 1):
        for subset in itertools.combinations(left_tranche, r):
            s = sum(subset)
            vault[s] = subset
            
    # CALCULATE BOUNDS FOR THE SIEVE
    min_vault = min(vault.keys())
    max_vault = max(vault.keys())
    
    print(f"    -> Vault Locked. {len(vault):,} entries.")
    print(f"    -> The Sieve: Only accepting targets between {min_vault} and {max_vault}")
    print(f"    -> RAM Fill Time: {time.time() - start_time:.2f}s")

    # PHASE B: THE HYDRA (Parallel Probing)
    print(f"[Phase B] Releasing The Hydra (Parallel CPU Scan)...")
    
    cpu_count = os.cpu_count() or 2
    print(f"    -> Detected {cpu_count} CPU Cores.")
    
    # Create Tasks: One task per subset size 'r'
    tasks = []
    for r in range(1, len(right_tranche) + 1):
        tasks.append((r, right_tranche, min_vault, max_vault))

    # Run Parallel Workers
    solution_found = False
    
    with multiprocessing.Pool(processes=cpu_count) as pool:
        for result_batch in pool.imap_unordered(worker_probe, tasks):
            if solution_found: break
            
            for target, right_subset in result_batch:
                # FINAL CHECK: Exact Hash Match
                if target in vault:
                    left_subset = vault[target]
                    
                    print(f"\n[!!!] GREENLIGHT! RESONANCE CONFIRMED.")
                    print(f"    Left Signal:  {target} (from {left_subset})")
                    print(f"    Right Signal: {-target} (from {right_subset})")
                    
                    full_solution = list(left_subset) + list(right_subset)
                    print(f"    Total Sum: {sum(full_solution)}")
                    print(f"    Solution Size: {len(full_solution)} numbers")
                    print(f"    Total Time: {time.time() - start_time:.4f}s")
                    
                    solution_found = True
                    pool.terminate()
                    return full_solution

    if not solution_found:
        print("[-] No resonance found.")
        return None

if __name__ == "__main__":
    # Standard Test: N=50
    problem = generate_titan(n=50) 
    solve_titan(problem)
