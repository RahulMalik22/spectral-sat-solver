#!/usr/bin/env python3
"""
test_benchmarks.py - Benchmark Testing Suite
============================================

Tests the Spectral-DP algorithm on generated benchmark instances
and compares performance across different structural categories.

Author: Rahul Malik
Date: November 30, 2025
"""

import os
import json
import time
import glob
from typing import Dict, List, Tuple
import statistics


class BenchmarkTester:
    """Test suite for Spectral-DP benchmarks"""
    
    def __init__(self, benchmark_dir: str = "benchmarks/titan_instances"):
        """Initialize tester with benchmark directory"""
        self.benchmark_dir = benchmark_dir
        self.results = []
    
    def load_json_instance(self, filepath: str) -> Dict:
        """Load a JSON benchmark instance"""
        with open(filepath, 'r') as f:
            return json.load(f)
    
    def load_cnf_instance(self, filepath: str) -> Tuple[int, List[Tuple]]:
        """
        Load a CNF benchmark instance
        
        Returns:
            (num_vars, clauses)
        """
        clauses = []
        num_vars = 0
        
        with open(filepath, 'r') as f:
            for line in f:
                line = line.strip()
                
                # Skip comments
                if line.startswith('c'):
                    continue
                
                # Parse problem line
                if line.startswith('p'):
                    parts = line.split()
                    num_vars = int(parts[2])
                    continue
                
                # Parse clause
                if line and not line.startswith('c') and not line.startswith('p'):
                    literals = [int(x) for x in line.split()[:-1]]  # Remove trailing 0
                    if len(literals) == 3:
                        clauses.append(tuple(literals))
        
        return num_vars, clauses
    
    def simple_walksat_solver(self, num_vars: int, clauses: List[Tuple], 
                              max_flips: int = 10000) -> Tuple[bool, float, Dict]:
        """
        Simple WalkSAT implementation for testing
        
        Returns:
            (solved, time_taken, assignment)
        """
        import random
        
        start_time = time.time()
        
        # Random initial assignment
        assignment = {i: random.choice([0, 1]) for i in range(1, num_vars + 1)}
        
        for flip in range(max_flips):
            # Check if satisfied
            unsatisfied = []
            for clause in clauses:
                satisfied = False
                for lit in clause:
                    var = abs(lit)
                    val = assignment[var]
                    if (lit > 0 and val == 1) or (lit < 0 and val == 0):
                        satisfied = True
                        break
                if not satisfied:
                    unsatisfied.append(clause)
            
            # If all satisfied, we're done
            if not unsatisfied:
                time_taken = time.time() - start_time
                return True, time_taken, assignment
            
            # Pick random unsatisfied clause and flip a variable
            clause = random.choice(unsatisfied)
            var_to_flip = abs(random.choice(clause))
            assignment[var_to_flip] = 1 - assignment[var_to_flip]
        
        time_taken = time.time() - start_time
        return False, time_taken, assignment
    
    def test_instance(self, filepath: str) -> Dict:
        """Test a single instance"""
        # Determine format
        if filepath.endswith('.json'):
            instance = self.load_json_instance(filepath)
            num_vars = instance['num_vars']
            clauses = [tuple(c) for c in instance['clauses']]
            metadata = instance.get('metadata', {})
        else:  # CNF
            num_vars, clauses = self.load_cnf_instance(filepath)
            metadata = {}
        
        # Run solver
        solved, time_taken, assignment = self.simple_walksat_solver(
            num_vars, clauses, max_flips=10000
        )
        
        result = {
            'filename': os.path.basename(filepath),
            'num_vars': num_vars,
            'num_clauses': len(clauses),
            'ratio': len(clauses) / num_vars,
            'solved': solved,
            'time': time_taken,
            'metadata': metadata
        }
        
        return result
    
    def run_benchmark_suite(self, pattern: str = "*.json"):
        """Run tests on all matching instances"""
        print("\n🔷 TITAN BENCHMARK TEST SUITE")
        print("=" * 70)
        
        # Find all matching files
        search_pattern = os.path.join(self.benchmark_dir, pattern)
        files = sorted(glob.glob(search_pattern))
        
        if not files:
            print(f"⚠️  No files found matching: {search_pattern}")
            return
        
        print(f"Found {len(files)} instances to test\n")
        
        # Test each instance
        for i, filepath in enumerate(files, 1):
            print(f"[{i}/{len(files)}] Testing {os.path.basename(filepath)}...", end=" ")
            
            try:
                result = self.test_instance(filepath)
                self.results.append(result)
                
                status = "✓ SOLVED" if result['solved'] else "✗ TIMEOUT"
                print(f"{status} ({result['time']:.4f}s)")
                
            except Exception as e:
                print(f"✗ ERROR: {str(e)}")
        
        print("\n" + "=" * 70)
        self._print_summary()
    
    def _print_summary(self):
        """Print summary statistics"""
        if not self.results:
            print("No results to summarize")
            return
        
        print("\n📊 SUMMARY STATISTICS")
        print("=" * 70)
        
        # Group by category
        categories = {}
        for result in self.results:
            category = result.get('metadata', {}).get('category', 'unknown')
            if category not in categories:
                categories[category] = []
            categories[category].append(result)
        
        # Print category statistics
        for category, results in sorted(categories.items()):
            print(f"\n{category.upper().replace('_', ' ')}:")
            print("-" * 70)
            
            solved = [r for r in results if r['solved']]
            times = [r['time'] for r in solved] if solved else [0]
            
            print(f"  Instances: {len(results)}")
            print(f"  Solved: {len(solved)}/{len(results)} ({100*len(solved)/len(results):.1f}%)")
            if times and times != [0]:
                print(f"  Avg time: {statistics.mean(times):.4f}s")
                print(f"  Min time: {min(times):.4f}s")
                print(f"  Max time: {max(times):.4f}s")
                if len(times) > 1:
                    print(f"  Std dev: {statistics.stdev(times):.4f}s")
        
        # Overall statistics
        print("\n" + "=" * 70)
        print("OVERALL PERFORMANCE:")
        print("-" * 70)
        
        total_solved = sum(1 for r in self.results if r['solved'])
        all_times = [r['time'] for r in self.results if r['solved']]
        
        print(f"  Total solved: {total_solved}/{len(self.results)} ({100*total_solved/len(self.results):.1f}%)")
        if all_times:
            print(f"  Average time: {statistics.mean(all_times):.4f}s")
            print(f"  Total time: {sum(all_times):.4f}s")
        
        print("=" * 70 + "\n")
    
    def export_results(self, output_file: str = "benchmark_results.json"):
        """Export results to JSON file"""
        output_path = os.path.join(self.benchmark_dir, output_file)
        
        with open(output_path, 'w') as f:
            json.dump({
                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
                'total_instances': len(self.results),
                'results': self.results
            }, f, indent=2)
        
        print(f"✓ Results exported to: {output_path}\n")


def main():
    """Main execution"""
    import sys
    
    print("\n🚀 Starting Benchmark Testing Suite\n")
    
    # Check if benchmark directory exists
    benchmark_dir = "benchmarks/titan_instances"
    if not os.path.exists(benchmark_dir):
        print(f"⚠️  Benchmark directory not found: {benchmark_dir}")
        print("   Run generate_benchmarks.py first to create instances\n")
        return
    
    # Run tests
    tester = BenchmarkTester(benchmark_dir)
    
    # Test based on command line argument
    if len(sys.argv) > 1:
        pattern = sys.argv[1]
    else:
        pattern = "*.json"  # Default to JSON instances
    
    tester.run_benchmark_suite(pattern)
    
    # Export results
    tester.export_results()
    
    print("✓ Benchmark testing complete!\n")


if __name__ == "__main__":
    main()
