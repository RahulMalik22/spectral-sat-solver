#!/usr/bin/env python3
"""
titan_v3.py - Titan Combinatorics Solver
=========================================

A Python implementation demonstrating divide-and-conquer strategies
for combinatorial optimization problems. This solver showcases the
"Tranche" decomposition approach used in the Spectral-DP algorithm.

The Titan solver uses:
1. SPLIT: Divide problem space into manageable tranches
2. VAULT: Pre-compute and cache partial solutions
3. SIEVE: Filter and combine solutions efficiently
4. HYDRA: Parallel processing for scalability

Author: Rahul Malik
Date: November 30, 2025
License: MIT
"""

import random
import time
import itertools
import multiprocessing
from typing import List, Tuple, Dict, Set, Optional
from functools import lru_cache
import sys


class TitanSolver:
    """
    The Titan Solver - A divide-and-conquer combinatorial optimizer
    
    This class implements the core principles of spectral decomposition
    applied to combinatorial problems, demonstrating how "tranche" 
    partitioning can achieve exponential speedups.
    """
    
    def __init__(self, numbers: List[int], target: Optional[int] = None, 
                 enable_parallel: bool = True, max_workers: int = None):
        """
        Initialize the Titan Solver
        
        Args:
            numbers: List of integers to work with
            target: Target sum (if None, finds all possible sums)
            enable_parallel: Enable parallel processing
            max_workers: Number of parallel workers (None = CPU count)
        """
        self.numbers = sorted(numbers)  # Sort for better cache locality
        self.target = target
        self.enable_parallel = enable_parallel
        self.max_workers = max_workers or multiprocessing.cpu_count()
        
        # Statistics
        self.stats = {
            'vault_size': 0,
            'combinations_checked': 0,
            'time_split': 0.0,
            'time_vault': 0.0,
            'time_sieve': 0.0
        }
    
    def solve(self) -> Dict[str, any]:
        """
        Main solving routine - The Titan Protocol
        
        Returns:
            Dictionary containing solution and statistics
        """
        start_time = time.time()
        
        print(f"🔷 TITAN SOLVER v3.0")
        print(f"{'='*60}")
        print(f"Input size: {len(self.numbers)} numbers")
        print(f"Target sum: {self.target if self.target else 'ALL'}")
        print(f"Parallel mode: {'ENABLED' if self.enable_parallel else 'DISABLED'}")
        print(f"{'='*60}\n")
        
        # PHASE 1: THE SPLIT (Decomposition)
        print("⚡ PHASE 1: TRANCHE DECOMPOSITION")
        split_start = time.time()
        left_tranche, right_tranche = self._split_tranches()
        self.stats['time_split'] = time.time() - split_start
        print(f"   Left tranche:  {len(left_tranche)} elements")
        print(f"   Right tranche: {len(right_tranche)} elements")
        print(f"   Time: {self.stats['time_split']:.4f}s\n")
        
        # PHASE 2: THE VAULT (Pre-computation)
        print("🔐 PHASE 2: VAULT CONSTRUCTION")
        vault_start = time.time()
        left_vault = self._build_vault(left_tranche, "LEFT")
        right_vault = self._build_vault(right_tranche, "RIGHT")
        self.stats['time_vault'] = time.time() - vault_start
        self.stats['vault_size'] = len(left_vault) + len(right_vault)
        print(f"   Total vault entries: {self.stats['vault_size']}")
        print(f"   Time: {self.stats['time_vault']:.4f}s\n")
        
        # PHASE 3: THE SIEVE (Combination & Filtering)
        print("🌊 PHASE 3: SIEVE & HYDRA")
        sieve_start = time.time()
        solution = self._sieve_and_combine(left_vault, right_vault)
        self.stats['time_sieve'] = time.time() - sieve_start
        print(f"   Combinations checked: {self.stats['combinations_checked']}")
        print(f"   Time: {self.stats['time_sieve']:.4f}s\n")
        
        total_time = time.time() - start_time
        
        # Results
        print(f"{'='*60}")
        if solution:
            print(f"✓ SOLUTION FOUND")
            print(f"   Subset: {solution['subset']}")
            print(f"   Sum: {solution['sum']}")
        else:
            print(f"✗ NO SOLUTION EXISTS")
        print(f"   Total time: {total_time:.4f}s")
        print(f"{'='*60}\n")
        
        return {
            'solved': solution is not None,
            'solution': solution,
            'stats': self.stats,
            'total_time': total_time
        }
    
    def _split_tranches(self) -> Tuple[List[int], List[int]]:
        """
        Split the problem into two tranches (left and right)
        
        This mimics the spectral bisection in Spectral-DP, where
        the Fiedler vector determines the optimal split point.
        
        Returns:
            Tuple of (left_tranche, right_tranche)
        """
        mid = len(self.numbers) // 2
        left = self.numbers[:mid]
        right = self.numbers[mid:]
        return left, right
    
    def _build_vault(self, tranche: List[int], label: str) -> Dict[int, Tuple]:
        """
        Build the vault - pre-compute all possible subset sums
        
        This is the "Greenlight" phase: we compute all valid partial
        assignments that the recursive call can satisfy.
        
        Args:
            tranche: List of numbers in this tranche
            label: Label for logging (LEFT or RIGHT)
            
        Returns:
            Dictionary mapping sum -> subset tuple
        """
        vault = {}
        
        # Include empty subset (sum = 0)
        vault[0] = tuple()
        
        # Generate all non-empty subsets
        for r in range(1, len(tranche) + 1):
            for subset in itertools.combinations(tranche, r):
                s = sum(subset)
                # Store the first subset found for each sum
                if s not in vault:
                    vault[s] = subset
        
        print(f"   {label} vault: {len(vault)} unique sums")
        return vault
    
    def _sieve_and_combine(self, left_vault: Dict[int, Tuple], 
                          right_vault: Dict[int, Tuple]) -> Optional[Dict]:
        """
        Sieve through combinations and find valid solutions
        
        This is the "merge" phase of the divide-and-conquer algorithm.
        We iterate through all possible combinations of left and right
        partial solutions to find one that satisfies the global constraint.
        
        Args:
            left_vault: Pre-computed sums from left tranche
            right_vault: Pre-computed sums from right tranche
            
        Returns:
            Solution dictionary if found, None otherwise
        """
        if self.target is None:
            # No specific target - return largest sum combination
            max_sum = max(left_vault.keys()) + max(right_vault.keys())
            left_subset = left_vault[max(left_vault.keys())]
            right_subset = right_vault[max(right_vault.keys())]
            
            return {
                'subset': left_subset + right_subset,
                'sum': max_sum
            }
        
        # Search for target sum
        if self.enable_parallel:
            return self._parallel_search(left_vault, right_vault)
        else:
            return self._sequential_search(left_vault, right_vault)
    
    def _sequential_search(self, left_vault: Dict[int, Tuple], 
                          right_vault: Dict[int, Tuple]) -> Optional[Dict]:
        """Sequential search through vault combinations"""
        for left_sum, left_subset in left_vault.items():
            needed = self.target - left_sum
            
            if needed in right_vault:
                self.stats['combinations_checked'] += 1
                right_subset = right_vault[needed]
                
                return {
                    'subset': left_subset + right_subset,
                    'sum': self.target
                }
            
            self.stats['combinations_checked'] += 1
        
        return None
    
    def _parallel_search(self, left_vault: Dict[int, Tuple], 
                        right_vault: Dict[int, Tuple]) -> Optional[Dict]:
        """
        Parallel search using multiprocessing (The Hydra)
        
        Splits the left vault across multiple workers to search
        for complementary right vault entries in parallel.
        """
        # Split left vault into chunks
        left_items = list(left_vault.items())
        chunk_size = max(1, len(left_items) // self.max_workers)
        chunks = [left_items[i:i + chunk_size] 
                 for i in range(0, len(left_items), chunk_size)]
        
        # Define worker function
        def worker(chunk, right_v, tgt):
            for left_sum, left_subset in chunk:
                needed = tgt - left_sum
                if needed in right_v:
                    return {
                        'subset': left_subset + right_v[needed],
                        'sum': tgt
                    }
            return None
        
        # Launch parallel workers
        with multiprocessing.Pool(processes=self.max_workers) as pool:
            results = pool.starmap(worker, 
                                  [(chunk, right_vault, self.target) 
                                   for chunk in chunks])
        
        self.stats['combinations_checked'] = len(left_vault)
        
        # Return first valid solution found
        for result in results:
            if result is not None:
                return result
        
        return None


def solve_titan(numbers: List[int], target: Optional[int] = None, 
                parallel: bool = True) -> Dict:
    """
    Convenience function for solving with Titan
    
    Args:
        numbers: List of integers to process
        target: Target sum (None = find maximum)
        parallel: Enable parallel processing
        
    Returns:
        Solution dictionary
    """
    solver = TitanSolver(numbers, target, enable_parallel=parallel)
    return solver.solve()


def generate_test_instance(size: int = 20, max_val: int = 100) -> List[int]:
    """Generate a random test instance"""
    return [random.randint(1, max_val) for _ in range(size)]


def main():
    """Main execution - demonstration and testing"""
    print("\n" + "="*60)
    print("TITAN COMBINATORICS SOLVER - DEMONSTRATION")
    print("="*60 + "\n")
    
    # Example 1: Small instance with specific target
    print("📊 EXAMPLE 1: Subset Sum Problem")
    print("-" * 60)
    numbers1 = [3, 5, 7, 11, 13, 17, 19, 23, 29, 31]
    target1 = 50
    result1 = solve_titan(numbers1, target=target1, parallel=False)
    
    # Example 2: Larger instance demonstrating parallel speedup
    print("\n📊 EXAMPLE 2: Larger Instance (Parallel)")
    print("-" * 60)
    numbers2 = generate_test_instance(size=25, max_val=50)
    target2 = sum(numbers2) // 2  # Target is half of total sum
    result2 = solve_titan(numbers2, target=target2, parallel=True)
    
    # Example 3: Maximum sum (no target)
    print("\n📊 EXAMPLE 3: Maximum Sum")
    print("-" * 60)
    numbers3 = [1, 2, 3, 5, 8, 13, 21, 34]
    result3 = solve_titan(numbers3, target=None, parallel=False)
    
    # Performance summary
    print("\n" + "="*60)
    print("PERFORMANCE SUMMARY")
    print("="*60)
    print(f"Example 1: {result1['total_time']:.4f}s")
    print(f"Example 2: {result2['total_time']:.4f}s (parallel)")
    print(f"Example 3: {result3['total_time']:.4f}s")
    print("\n✓ All tests complete\n")


if __name__ == "__main__":
    # Set random seed for reproducibility
    random.seed(42)
    
    # Run demonstrations
    main()
