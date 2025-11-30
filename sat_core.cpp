#include <iostream>
#include <vector>
#include <cstdlib>
#include <ctime>
#include <cmath>

extern "C" {

    // Representation:
    // Variables are 1 to N.
    // A literal is represented as an int. Positive = True, Negative = False.
    // Clause: [1, -2, 3] means (x1 OR NOT x2 OR x3)

    // Check if a specific assignment satisfies all clauses
    // assignment: array of size N+1. assignment[i] is 0 (False) or 1 (True).
    int count_unsatisfied(int* clauses, int num_clauses, int* assignment) {
        int unsatisfied = 0;
        
        // Each clause has 3 literals. Array is flat: [c1_a, c1_b, c1_c, c2_a...]
        for (int i = 0; i < num_clauses; ++i) {
            bool clause_true = false;
            for (int j = 0; j < 3; ++j) {
                int lit = clauses[i * 3 + j];
                int var = abs(lit);
                int val = assignment[var];
                
                // If lit is positive, we need val=1. If lit is negative, we need val=0.
                if ((lit > 0 && val == 1) || (lit < 0 && val == 0)) {
                    clause_true = true;
                    break; // Short circuit: Clause is happy
                }
            }
            if (!clause_true) unsatisfied++;
        }
        return unsatisfied;
    }

    // WALKSAT (The "Chaos" Solver)
    // Tries to fix random broken clauses by flipping variables.
    // Returns 1 if solved, 0 if failed.
    int walk_sat(int* clauses, int num_clauses, int num_vars, int* assignment, int max_flips) {
        
        // Random Initialization
        for(int i=1; i<=num_vars; i++) assignment[i] = rand() % 2;
        
        for (int flip = 0; flip < max_flips; ++flip) {
            // 1. Check Score
            int bad_count = count_unsatisfied(clauses, num_clauses, assignment);
            if (bad_count == 0) return 1; // VICTORY!
            
            // 2. Pick a random broken clause (The "Tranche" we need to fix)
            int broken_clause_idx = -1;
            
            // Random start to avoid bias
            int start_idx = rand() % num_clauses;
            for(int k=0; k<num_clauses; k++) {
                int idx = (start_idx + k) % num_clauses;
                bool satisfied = false;
                for(int j=0; j<3; j++) {
                    int lit = clauses[idx*3 + j];
                    int val = assignment[abs(lit)];
                    if ((lit > 0 && val == 1) || (lit < 0 && val == 0)) {
                        satisfied = true; break;
                    }
                }
                if (!satisfied) {
                    broken_clause_idx = idx;
                    break;
                }
            }
            
            // 3. Pick a variable in that clause to flip
            // Heuristic: Pick the one that breaks the fewest OTHER clauses (Greedy)
            // Or pick random (Chaos)
            
            int best_var = -1;
            int best_score = 999999;
            
            // Probability to do random move (Noise/Salt)
            // 50% Chaos, 50% Greedy
            if ((rand() % 100) < 50) {
                // Randomly flip one of the 3 vars in the broken clause
                int r_lit = clauses[broken_clause_idx * 3 + (rand() % 3)];
                best_var = abs(r_lit);
            } else {
                // Greedy: Check all 3 vars, flip the best one
                for(int j=0; j<3; j++) {
                    int lit = clauses[broken_clause_idx * 3 + j];
                    int var = abs(lit);
                    
                    // Try flip
                    assignment[var] = 1 - assignment[var];
                    int score = count_unsatisfied(clauses, num_clauses, assignment);
                    assignment[var] = 1 - assignment[var]; // Flip back
                    
                    if (score < best_score) {
                        best_score = score;
                        best_var = var;
                    }
                }
            }
            
            // Execute the flip
            assignment[best_var] = 1 - assignment[best_var];
        }
        
        return 0; // Failed to solve in time
    }
}
