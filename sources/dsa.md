# Data Structures & Problem Solving — From Beginner to Expert

> A curriculum of **77 five-minute reads** organized into 4 progression tiers plus a cross-cutting Meta layer. Every entry: a mental model, when to use it, complexity, one code example, 2–3 classic problems, a pitfall, and a bridge to the next idea.

---

## How to Use This

1. **Don't read linearly.** Pick the tier matching your current ceiling. If you cannot solve LeetCode Mediums consistently, you belong in Tier 1–2 regardless of years of experience.
2. **One read = one topic = one solved problem.** Reading without coding is the #1 way to fool yourself into thinking you've learned.
3. **Spaced repetition.** Re-solve a topic's example problem 1 day later, 1 week later, 1 month later. If it doesn't come back fast, your "understanding" was illusory.
4. **The Meta tier is non-optional.** It's the difference between someone who knows 50 algorithms and someone who solves problems. Read it in parallel with Tier 2.

### Learning path

```
                               ┌──────────────────────────┐
                               │  META  (read alongside)  │
                               │  patterns, debugging,    │
                               │  reading problems        │
                               └──────────┬───────────────┘
                                          │
   Tier 1 BEGINNER ─► Tier 2 INTERMEDIATE ─► Tier 3 ADVANCED ─► Tier 4 EXPERT
   (foundations)     (interview-ready)      (contest-medium)   (red-coder/HFT)
   complexity,        trees, graphs,         DP, segment trees,  HLD, FFT, suffix
   arrays, hashing,   heaps, DSU, intervals  shortest paths      automaton, MCMF
```

---

## Curriculum Index

| Tier | # | Topic |
|---|---|---|
| **1 Beginner** | 1.1 | Big-O thinking |
|  | 1.2 | Arrays & dynamic arrays |
|  | 1.3 | Hash maps & sets |
|  | 1.4 | Two pointers |
|  | 1.5 | Sliding window |
|  | 1.6 | Stacks |
|  | 1.7 | Queues |
|  | 1.8 | Binary search |
|  | 1.9 | Recursion |
|  | 1.10 | Sorting basics |
|  | 1.11 | Linked lists |
| **2 Intermediate** | 2.1 | Tree traversals |
|  | 2.2 | Binary search trees |
|  | 2.3 | Graph representations |
|  | 2.4 | BFS / DFS |
|  | 2.5 | Topological sort |
|  | 2.6 | Heaps & priority queues |
|  | 2.7 | Backtracking |
|  | 2.8 | Greedy with proof |
|  | 2.9 | Bit manipulation |
|  | 2.10 | Prefix sums & difference arrays |
|  | 2.11 | Union-Find (DSU) |
|  | 2.12 | Tries |
|  | 2.13 | Monotonic stack/deque |
|  | 2.14 | Interval problems |
| **3 Advanced** | 3.1 | DP: first principles |
|  | 3.2 | 1D DP |
|  | 3.3 | 2D / grid DP |
|  | 3.4 | Knapsack family |
|  | 3.5 | Interval DP |
|  | 3.6 | Tree DP |
|  | 3.7 | Bitmask DP |
|  | 3.8 | Dijkstra |
|  | 3.9 | Bellman–Ford & SPFA |
|  | 3.10 | Floyd–Warshall |
|  | 3.11 | MST: Kruskal & Prim |
|  | 3.12 | Segment tree (point update) |
|  | 3.13 | Fenwick / BIT |
|  | 3.14 | Lazy propagation |
|  | 3.15 | KMP |
|  | 3.16 | Z-algorithm |
|  | 3.17 | Rabin–Karp |
|  | 3.18 | A* search |
| **4 Expert** | 4.1 | Heavy–light decomposition |
|  | 4.2 | Centroid decomposition |
|  | 4.3 | Persistent segment tree |
|  | 4.4 | Segment tree beats |
|  | 4.5 | Wavelet tree |
|  | 4.6 | Link–cut tree |
|  | 4.7 | Suffix array + LCP |
|  | 4.8 | Suffix automaton |
|  | 4.9 | Aho–Corasick |
|  | 4.10 | FFT / NTT |
|  | 4.11 | Min-cost max-flow |
|  | 4.12 | Hopcroft–Karp |
|  | 4.13 | 2-SAT |
|  | 4.14 | Convex hull trick / Li Chao |
|  | 4.15 | Digit DP |
|  | 4.16 | DP on broken profile |
|  | 4.17 | Mo's algorithm (with updates) |
|  | 4.18 | LCA: binary lifting & Euler tour |
|  | 4.19 | Sprague–Grundy / game theory |
|  | 4.20 | Randomized algorithms (hashing, treaps, reservoir) |
| **Meta (read in parallel)** | M.1 | How to read a problem |
|  | M.2 | Constraints → algorithm cheat sheet |
|  | M.3 | Always brute force first |
|  | M.4 | The 14 FAANG patterns |
|  | M.5 | Invariants & monovariants |
|  | M.6 | Reductions |
|  | M.7 | Stress testing |
|  | M.8 | DP state design |
|  | M.9 | Time–space tradeoffs |
|  | M.10 | Brute / Better / Best framework |
|  | M.11 | Mock interviews |
|  | M.12 | Deliberate practice |
|  | M.13 | Climbing ratings |
|  | M.14 | Reading editorials |

---

# TIER 1 — Beginner (foundations you cannot skip)

## 1.1 Big-O thinking
**Mental model.** Drop constants and lower-order terms; ask "how does the *time* grow as input grows?" Loops multiply, sequential code adds. `O(1) < O(log n) < O(n) < O(n log n) < O(n²) < O(2ⁿ) < O(n!)`.

**When.** Before you write code. Always estimate before coding.

**Complexity rule of thumb (1 sec @ ~10⁸ ops):**
- n ≤ 10: `O(n!)` ok
- n ≤ 20: `O(2ⁿ)`
- n ≤ 500: `O(n³)`
- n ≤ 5,000: `O(n²)`
- n ≤ 10⁶: `O(n log n)`
- n ≤ 10⁸: `O(n)` or `O(log n)`

**Example (Python).**
```python
# O(n) — single pass
def has_duplicate(a):
    seen = set()
    for x in a:
        if x in seen: return True
        seen.add(x)
    return False
```
**Classic problems.** Two Sum, Contains Duplicate, Maximum Subarray.
**Pitfall.** Hidden costs: `s in list` is `O(n)`, `s in set` is `O(1)`. String concatenation in a loop is `O(n²)`.
**Bridge → 1.2:** the data structure choice *is* the complexity.

## 1.2 Arrays & dynamic arrays
**Mental model.** A contiguous block of memory. Index access `O(1)`. Insert/delete at end *amortized* `O(1)`; in the middle `O(n)`.

**When.** Default container. If you don't know what to use, use an array.

**Example (Python).**
```python
a = [3, 1, 4, 1, 5]   # dynamic array (list)
a.append(9)           # O(1) amortized
a.pop()               # O(1)
a.insert(0, 7)        # O(n) — avoid
```
**Classic problems.** Move Zeros, Remove Duplicates from Sorted Array, Best Time to Buy/Sell Stock.
**Pitfall.** Repeated `del a[0]` is `O(n)` each time → `O(n²)`. Use a deque or two pointers.
**Bridge → 1.3:** when "lookup by value" matters, array isn't enough.

## 1.3 Hash maps & sets
**Mental model.** Average `O(1)` insert/lookup/delete via a hash function. Trades memory and ordering for speed.

**When.** "Have I seen this before?", counting frequencies, group by key.

**Example.**
```python
from collections import Counter, defaultdict
def two_sum(a, t):
    seen = {}
    for i, x in enumerate(a):
        if t - x in seen: return [seen[t-x], i]
        seen[x] = i
```
**Classic problems.** Two Sum, Group Anagrams, Longest Substring Without Repeating Characters, Top K Frequent Elements.
**Pitfall.** Worst-case `O(n)` per op with adversarial keys (rare in interviews, real in CP — see 4.20). Iteration order is insertion-order in Python 3.7+.
**Bridge → 1.4:** when the array is *sorted* you often don't need a hash map.

## 1.4 Two pointers
**Mental model.** Two indices walking the array, often from opposite ends or at different speeds, exploiting *sortedness* or *monotonicity*.

**When.** Sorted array problems; pair/triplet-sum; in-place partition; palindrome check.

**Example.**
```python
def two_sum_sorted(a, t):
    i, j = 0, len(a) - 1
    while i < j:
        s = a[i] + a[j]
        if s == t: return [i, j]
        if s < t: i += 1
        else:     j -= 1
```
**Classic problems.** 3Sum, Container With Most Water, Trapping Rain Water, Remove Duplicates Sorted.
**Pitfall.** Forgetting to skip duplicates → counting same triplet multiple times.
**Bridge → 1.5:** what if the window has variable size and slides?

## 1.5 Sliding window
**Mental model.** A range `[L, R]` over the array. Expand `R`; while invariant breaks, shrink `L`. Each element enters and leaves once → `O(n)`.

**When.** "Longest/shortest/count-of subarrays satisfying property X." Property must be *monotone* in window size.

**Example.**
```python
def longest_unique(s):
    last, L, best = {}, 0, 0
    for R, c in enumerate(s):
        if c in last and last[c] >= L:
            L = last[c] + 1
        last[c] = R
        best = max(best, R - L + 1)
    return best
```
**Classic problems.** Longest Substring Without Repeats, Min Window Substring, Subarrays with Sum K (positives), Permutation in String.
**Pitfall.** Negative numbers / non-monotone constraints break the technique → see prefix sums (2.10).
**Bridge → 1.6:** what if order matters, like matching brackets?

## 1.6 Stacks
**Mental model.** LIFO. Push/pop/top in `O(1)`. Useful for "last seen" or matching.

**When.** Bracket matching, expression evaluation, undo, DFS iterative, monotonic stack (2.13).

**Example.**
```python
def valid_parens(s):
    pair = {')':'(', ']':'[', '}':'{'}
    st = []
    for c in s:
        if c in '([{': st.append(c)
        elif not st or st.pop() != pair[c]: return False
    return not st
```
**Classic problems.** Valid Parentheses, Min Stack, Daily Temperatures (2.13), Evaluate RPN.
**Pitfall.** Forgetting to check stack non-empty before pop.
**Bridge → 1.7:** what if you want FIFO instead of LIFO?

## 1.7 Queues
**Mental model.** FIFO. Dequeue in `O(1)`. Use `collections.deque`, never `list.pop(0)`.

**When.** BFS, level-order traversal, scheduling, sliding window max (2.13).

**Example.**
```python
from collections import deque
def bfs_grid(g, sr, sc):
    R, C = len(g), len(g[0])
    seen = {(sr,sc)}
    q = deque([(sr,sc,0)])
    while q:
        r, c, d = q.popleft()
        # process...
        for dr, dc in [(-1,0),(1,0),(0,-1),(0,1)]:
            nr, nc = r+dr, c+dc
            if 0<=nr<R and 0<=nc<C and (nr,nc) not in seen and g[nr][nc] != '#':
                seen.add((nr,nc)); q.append((nr,nc,d+1))
```
**Classic problems.** Number of Islands (BFS), Rotting Oranges, Open the Lock.
**Pitfall.** Using `list.pop(0)` → `O(n²)` BFS. Forgetting to mark `seen` *before* pushing → exponential blowup.
**Bridge → 1.8:** when the search space is sorted, you can be smarter than scanning.

## 1.8 Binary search
**Mental model.** On a *monotone* function `f(x)`, halve the search space each step. `O(log n)`.

**Two patterns:**
1. **On array** — find an element / first ≥ x / last ≤ x.
2. **On answer** — binary search the answer; check feasibility.

**Example (binary search on answer — Koko Bananas).**
```python
def min_speed(piles, h):
    def hours(k): return sum((p + k - 1) // k for p in piles)
    lo, hi = 1, max(piles)
    while lo < hi:
        mid = (lo + hi) // 2
        if hours(mid) <= h: hi = mid
        else:               lo = mid + 1
    return lo
```
**Classic problems.** First Bad Version, Search in Rotated Sorted Array, Median of Two Sorted Arrays, Capacity to Ship Packages, Split Array Largest Sum.
**Pitfall.** Off-by-one. Pick *one* template (`lo<hi`, `hi=mid`, `lo=mid+1`) and use it everywhere. Test on size 0/1/2.
**Bridge → 1.9:** halving is a form of recursion.

## 1.9 Recursion
**Mental model.** Define base case and recursive case. Trust the function works on smaller inputs (the "leap of faith"). Stack depth = recursion depth.

**When.** Trees, divide-and-conquer, backtracking, DP (2.7, 3.x).

**Example (subsets).**
```python
def subsets(a):
    out = []
    def go(i, cur):
        if i == len(a): out.append(cur[:]); return
        go(i+1, cur)              # skip
        cur.append(a[i]); go(i+1, cur); cur.pop()  # take
    go(0, [])
    return out
```
**Classic problems.** Power Set, Permutations, Generate Parentheses, Reverse Linked List Recursive.
**Pitfall.** Stack overflow at depth ~1000 in Python — use `sys.setrecursionlimit` or convert to iteration. Mutating shared state without backtrack = bugs.
**Bridge → 1.10:** divide-and-conquer's flagship is sorting.

## 1.10 Sorting basics
**Mental model.** Comparison sorts have lower bound `Ω(n log n)`. Counting/radix sort beat that for bounded integers (`O(n + k)`).

**Algorithms to know:**
- **Merge sort** — stable, `O(n log n)`, `O(n)` extra memory; foundation for inversions.
- **Quick sort** — average `O(n log n)`, worst `O(n²)` (mitigated by random pivot).
- **Heap sort** — `O(n log n)`, in-place, not stable.
- **Counting/radix** — `O(n)` for small integer range.

**Example (custom comparator — sort by string concat to form largest number).**
```python
from functools import cmp_to_key
def largest_number(nums):
    s = list(map(str, nums))
    s.sort(key=cmp_to_key(lambda a,b: -1 if a+b > b+a else 1))
    return ''.join(s).lstrip('0') or '0'
```
**Classic problems.** Sort Colors (3-way), Merge Intervals, K Closest Points, Largest Number, Inversion Count.
**Pitfall.** `sorted(arr, key=...)` is stable; `arr.sort(key=...)` mutates in place. Custom comparator on floats — use a small epsilon.
**Bridge → 1.11:** what if the data isn't contiguous?

## 1.11 Linked lists
**Mental model.** Nodes with `next` pointers. `O(1)` insert/delete given a pointer; `O(n)` to find anything. *Owning* the previous pointer is what matters.

**Three core techniques:**
1. **Dummy head** — eliminates edge cases at the front.
2. **Slow/fast pointers** — find middle, detect cycle (Floyd's).
3. **Reversal** — three-pointer iterative.

**Example (reverse).**
```python
def reverse(head):
    prev, cur = None, head
    while cur:
        nxt = cur.next
        cur.next = prev
        prev, cur = cur, nxt
    return prev
```
**Classic problems.** Reverse Linked List, Merge Two Sorted Lists, Linked List Cycle (Floyd's), Reorder List, LRU Cache (with hashmap).
**Pitfall.** Losing the next pointer before reassigning. Always draw the diagram for 3 nodes; don't reason in your head.
**Bridge → Tier 2:** branching pointers → trees and graphs.

---

# TIER 2 — Intermediate (interview-ready)

## 2.1 Tree traversals
**Mental model.** Visit every node exactly once. Three DFS orders (pre/in/post) and one BFS (level).

**Example.**
```python
def inorder(root):
    if not root: return
    inorder(root.left); print(root.val); inorder(root.right)

def levelorder(root):
    from collections import deque
    q, out = deque([root]), []
    while q:
        lvl = []
        for _ in range(len(q)):
            n = q.popleft()
            if n: lvl.append(n.val); q.append(n.left); q.append(n.right)
        if lvl: out.append(lvl)
    return out
```
**Classic problems.** Max Depth, Same Tree, Path Sum, Symmetric Tree, Binary Tree Level Order, Construct Tree from Preorder + Inorder.
**Pitfall.** Iterative inorder is the trickiest — practice it.
**Bridge → 2.2:** when the tree has order, search becomes logarithmic (on balance).

## 2.2 Binary search trees
**Mental model.** For every node: `left < node < right`. Operations are `O(h)` where `h` is height — `O(log n)` if balanced, `O(n)` worst case.

**When.** When you need *ordered* hash-map-like operations: range queries, k-th element, predecessor/successor. Pure BSTs are rarely interview material; the *invariant* and *successor* are what matter. In practice, use `SortedList` (Python's `sortedcontainers`) or `std::set` (C++).

**Example (validate BST).**
```python
def is_bst(root, lo=float('-inf'), hi=float('inf')):
    if not root: return True
    if not (lo < root.val < hi): return False
    return is_bst(root.left, lo, root.val) and is_bst(root.right, root.val, hi)
```
**Classic problems.** Validate BST, Kth Smallest in BST, Lowest Common Ancestor of BST, Recover BST.
**Pitfall.** Equal values — pick a convention (strict `<` everywhere) and stick to it.
**Bridge → 2.3:** trees are graphs without cycles.

## 2.3 Graph representations
**Mental model.** A graph = (V, E). Three storage choices:
- **Adjacency list** — `dict[u] -> list[v]`. Best general purpose. `O(V + E)` space.
- **Adjacency matrix** — `M[u][v]`. `O(V²)` space; `O(1)` edge lookup. Use for dense small graphs.
- **Edge list** — `[(u,v,w)]`. Use for Kruskal, Bellman–Ford.

**Example.**
```python
from collections import defaultdict
def build_graph(n, edges):
    g = defaultdict(list)
    for u, v, w in edges:
        g[u].append((v, w))
        g[v].append((u, w))   # undirected
    return g
```
**Pitfall.** Forgetting directionality. Forgetting to handle disconnected components (loop over all vertices).
**Bridge → 2.4:** how do we visit all vertices?

## 2.4 BFS / DFS
**Mental model.**
- **BFS** — queue, level-by-level, gives shortest path in **unweighted** graphs.
- **DFS** — stack/recursion, depth-first, gives connectivity, cycle detection, topological order.

**Example (DFS connected components).**
```python
def num_components(n, g):
    seen = [False]*n
    cnt = 0
    def dfs(u):
        seen[u] = True
        for v in g[u]:
            if not seen[v]: dfs(v)
    for u in range(n):
        if not seen[u]: cnt += 1; dfs(u)
    return cnt
```
**Classic problems.** Number of Islands, Word Ladder (BFS), Course Schedule (cycle), Clone Graph, Pacific Atlantic, Surrounded Regions.
**Pitfall.** BFS on weighted graph gives wrong shortest path — use Dijkstra (3.8).
**Bridge → 2.5:** ordering nodes by dependency.

## 2.5 Topological sort
**Mental model.** Linear ordering of DAG vertices such that for every edge `u→v`, `u` comes before `v`. Two algorithms: **Kahn's** (BFS on in-degree 0) and **DFS post-order reversed**.

**Example (Kahn's).**
```python
from collections import deque, defaultdict
def topo(n, edges):
    g, indeg = defaultdict(list), [0]*n
    for u, v in edges:
        g[u].append(v); indeg[v] += 1
    q = deque(i for i in range(n) if indeg[i] == 0)
    out = []
    while q:
        u = q.popleft(); out.append(u)
        for v in g[u]:
            indeg[v] -= 1
            if indeg[v] == 0: q.append(v)
    return out if len(out) == n else []   # cycle if not all included
```
**Classic problems.** Course Schedule I & II, Alien Dictionary, Parallel Courses.
**Pitfall.** Topological sort is undefined on graphs with cycles — always check.
**Bridge → 2.6:** what if instead of any order, we want minimum/maximum?

## 2.6 Heaps & priority queues
**Mental model.** A complete binary tree with the heap property. `push` / `pop` in `O(log n)`, `top` in `O(1)`, `heapify` in `O(n)`.

**When.** Top-k, scheduling, Dijkstra, merge k sorted lists, median maintenance.

**Example (top-k frequent).**
```python
import heapq
from collections import Counter
def topk(a, k):
    c = Counter(a)
    return [x for x, _ in heapq.nlargest(k, c.items(), key=lambda kv: kv[1])]
```
**Classic problems.** Kth Largest, Merge K Sorted Lists, Find Median from Data Stream (two heaps), Task Scheduler, Reorganize String.
**Pitfall.** Python's `heapq` is min-heap only — negate for max-heap. For tuples, all fields must be comparable.
**Bridge → 2.7:** when the search tree is exponential, prune.

## 2.7 Backtracking
**Mental model.** DFS through the *decision tree*. Try a choice, recurse, undo. Prune impossible branches as early as possible.

**Template.**
```python
def backtrack(state):
    if is_solution(state): record(state); return
    for choice in choices(state):
        if not feasible(choice, state): continue
        apply(choice, state)
        backtrack(state)
        undo(choice, state)
```
**Example (N-Queens).**
```python
def n_queens(n):
    cols, d1, d2, sol = set(), set(), set(), []
    def go(r, board):
        if r == n: sol.append(board[:]); return
        for c in range(n):
            if c in cols or (r-c) in d1 or (r+c) in d2: continue
            cols.add(c); d1.add(r-c); d2.add(r+c); board.append(c)
            go(r+1, board)
            cols.remove(c); d1.remove(r-c); d2.remove(r+c); board.pop()
    go(0, [])
    return sol
```
**Classic problems.** N-Queens, Sudoku Solver, Word Search, Combination Sum, Permutations II, Letter Combinations.
**Pitfall.** Forgetting to undo state. Slicing lists `cur[:]` to copy is necessary when storing.
**Bridge → 2.8:** sometimes the optimal local choice *is* the global solution.

## 2.8 Greedy with proof
**Mental model.** Make the locally best choice. Works *only when* an exchange argument or matroid structure guarantees optimality.

**Two proof techniques:**
- **Exchange argument** — if there's a better solution, you can transform it into the greedy one without loss.
- **Stays-ahead** — at every step the greedy is at least as good as any other.

**Example (interval scheduling — max non-overlapping).**
```python
def max_meetings(intervals):
    intervals.sort(key=lambda x: x[1])   # sort by END
    end, cnt = float('-inf'), 0
    for s, e in intervals:
        if s >= end: cnt += 1; end = e
    return cnt
```
**Classic problems.** Activity Selection, Jump Game II, Gas Station, Task Scheduler, Minimum Number of Arrows to Burst Balloons.
**Pitfall.** Untested greediness — most "obvious" greedy ideas are wrong (counterexample: coin change with coins {1,3,4} for amount 6).
**Bridge → 2.9:** sometimes the operations themselves are bitwise.

## 2.9 Bit manipulation
**Mental model.** Treat ints as bitsets. Operations: `&` (and), `|` (or), `^` (xor), `~` (not), `<<` `>>` (shift). XOR with itself = 0; XOR with 0 = self.

**Tricks worth memorizing:**
- `x & (x-1)` → clears lowest set bit.
- `x & -x` → isolates lowest set bit.
- `x ^ y` → bits where they differ.
- `(x >> i) & 1` → i-th bit.
- Iterate subsets of mask: `s = m; while s > 0: ...; s = (s - 1) & m`.

**Example (single number — every other appears twice).**
```python
def single_number(a):
    r = 0
    for x in a: r ^= x
    return r
```
**Classic problems.** Single Number I/II/III, Number of 1 Bits, Counting Bits, Sum of Two Integers without `+`, Maximum XOR (with trie).
**Pitfall.** Negative numbers in Python are arbitrary precision — use `& 0xFFFFFFFF` for fixed-width emulation.
**Bridge → 2.10:** XOR is to addition what...

## 2.10 Prefix sums & difference arrays
**Mental model.** Precompute `P[i] = a[0] + a[1] + ... + a[i-1]`. Range sum `[l, r] = P[r+1] - P[l]` in `O(1)` after `O(n)` build.

**Difference array** is the *inverse*: range update in `O(1)`, point query at end in `O(n)`.

**Example (subarray sum equals K).**
```python
from collections import defaultdict
def subarray_sum(a, k):
    cnt = defaultdict(int); cnt[0] = 1
    s, ans = 0, 0
    for x in a:
        s += x
        ans += cnt[s - k]
        cnt[s] += 1
    return ans
```
**Classic problems.** Subarray Sum = K, Range Sum Query Immutable, Range Sum 2D, Number of Subarrays with Bounded Max, Continuous Subarray Sum.
**Pitfall.** Mixing 0-indexed and 1-indexed prefix sums in your head. Use `P[0] = 0`.
**Bridge → 2.11:** what about *grouping* values rather than summing?

## 2.11 Union-Find (DSU)
**Mental model.** Disjoint sets supporting `find(x)` (which set?) and `union(x, y)` (merge). With path compression + union by rank/size, both `O(α(n))` ≈ `O(1)`.

**Example.**
```python
class DSU:
    def __init__(self, n):
        self.p = list(range(n)); self.sz = [1]*n
    def find(self, x):
        while self.p[x] != x:
            self.p[x] = self.p[self.p[x]]   # path compression
            x = self.p[x]
        return x
    def union(self, a, b):
        a, b = self.find(a), self.find(b)
        if a == b: return False
        if self.sz[a] < self.sz[b]: a, b = b, a
        self.p[b] = a; self.sz[a] += self.sz[b]
        return True
```
**Classic problems.** Number of Connected Components, Redundant Connection, Accounts Merge, Most Stones Removed, Kruskal's MST.
**Pitfall.** Forgetting path compression makes it `O(log n)` per op. Don't use rank *and* size — pick one.
**Bridge → 2.12:** strings are also a kind of tree.

## 2.12 Tries
**Mental model.** A 26-ary tree (or more) where each path from root encodes a string. Insert/lookup/prefix in `O(L)` where `L` is word length.

**Example.**
```python
class Trie:
    def __init__(self): self.r = {}
    def insert(self, w):
        n = self.r
        for c in w: n = n.setdefault(c, {})
        n['$'] = True
    def starts_with(self, p):
        n = self.r
        for c in p:
            if c not in n: return False
            n = n[c]
        return True
```
**Classic problems.** Implement Trie, Word Search II, Replace Words, Maximum XOR (binary trie), Design Search Autocomplete.
**Pitfall.** Memory blowup — use arrays of 26 only when alphabet is fixed and small. Else use dict.
**Bridge → 2.13:** sometimes the data structure tracks *order* rather than membership.

## 2.13 Monotonic stack/deque
**Mental model.** A stack/deque kept in increasing or decreasing order — when pushing, pop violators first. Each element pushed/popped at most once → amortized `O(n)`.

**When.** "Next greater/smaller element," "max in sliding window," largest rectangle in histogram, stock span.

**Example (next greater element).**
```python
def next_greater(a):
    n = len(a); res = [-1]*n; st = []
    for i, x in enumerate(a):
        while st and a[st[-1]] < x:
            res[st.pop()] = x
        st.append(i)
    return res
```
**Example (sliding window max — monotonic deque).**
```python
from collections import deque
def max_window(a, k):
    dq, out = deque(), []
    for i, x in enumerate(a):
        while dq and a[dq[-1]] <= x: dq.pop()
        dq.append(i)
        if dq[0] <= i - k: dq.popleft()
        if i >= k - 1: out.append(a[dq[0]])
    return out
```
**Classic problems.** Daily Temperatures, Next Greater II, Largest Rectangle in Histogram, Sliding Window Max, Sum of Subarray Minimums.
**Pitfall.** Mixing strict/non-strict comparisons changes which duplicates are kept.
**Bridge → 2.14:** intervals are 1D ranges with extra structure.

## 2.14 Interval problems
**Mental model.** Three transformations cover most interval problems:
1. **Sort by start** — for merging.
2. **Sort by end** — for greedy scheduling (2.8).
3. **Sweep line / events** — sort `(point, +1/−1)`, scan, accumulate.

**Example (merge intervals).**
```python
def merge(iv):
    iv.sort()
    out = []
    for s, e in iv:
        if out and s <= out[-1][1]: out[-1][1] = max(out[-1][1], e)
        else: out.append([s, e])
    return out
```
**Example (meeting rooms II — sweep line).**
```python
def min_rooms(iv):
    ev = []
    for s, e in iv: ev.append((s, +1)); ev.append((e, -1))
    ev.sort()
    cur, best = 0, 0
    for _, d in ev: cur += d; best = max(best, cur)
    return best
```
**Classic problems.** Merge Intervals, Insert Interval, Meeting Rooms I & II, Non-overlapping Intervals, Employee Free Time.
**Pitfall.** Tie-breaking when start == end; decide whether closed/open.
**Bridge → Tier 3:** what if the optimal answer requires combining many sub-decisions?

---

# TIER 3 — Advanced (DP, shortest paths, segment trees)

## 3.1 DP: first principles
**Mental model.** Solve a problem by combining solutions to overlapping subproblems. Two requirements: **optimal substructure** (optimal whole built from optimal parts) + **overlapping subproblems** (same subproblem queried many times).

**Method.** (1) define a state `f(...)` that captures *exactly enough* to make a decision. (2) Recurrence relating `f(state)` to smaller states. (3) Base cases. (4) Top-down (memoization) or bottom-up (table). (5) Trace dependencies → iteration order.

**The 1-line test.** *Can the optimal answer be reconstructed from optimal answers to smaller versions of the same problem?* If yes, DP. If "smallest" is hard to define, you don't have a DP yet.

**Example (Fibonacci, both styles).**
```python
def fib_top(n, memo={}):
    if n < 2: return n
    if n in memo: return memo[n]
    memo[n] = fib_top(n-1) + fib_top(n-2); return memo[n]

def fib_bot(n):
    if n < 2: return n
    a, b = 0, 1
    for _ in range(n - 1): a, b = b, a + b
    return b
```
**Pitfall.** Wrong state. Add or remove a dimension *deliberately* (see M.8).
**Bridge → 3.2:** simplest case is a 1D state.

## 3.2 1D DP
**Mental model.** State = single index; recurrence looks back O(1) or O(n) steps.

**Example (House Robber).**
```python
def rob(nums):
    p, c = 0, 0
    for x in nums:
        p, c = c, max(c, p + x)
    return c
```
**Example (Longest Increasing Subsequence — `O(n log n)`).**
```python
from bisect import bisect_left
def lis(a):
    tails = []
    for x in a:
        i = bisect_left(tails, x)
        if i == len(tails): tails.append(x)
        else: tails[i] = x
    return len(tails)
```
**Classic problems.** House Robber I/II, Climbing Stairs, Decode Ways, LIS, Word Break, Coin Change (1D).
**Pitfall.** Using only the last value when you actually need 2 prior states (Robber needs `p` *and* `c`).
**Bridge → 3.3:** add a dimension.

## 3.3 2D / grid DP
**Mental model.** State = `(i, j)`; transitions usually from neighbors `(i-1, j)` or `(i, j-1)`.

**Example (Unique Paths).**
```python
def unique_paths(m, n):
    dp = [[1]*n for _ in range(m)]
    for i in range(1, m):
        for j in range(1, n):
            dp[i][j] = dp[i-1][j] + dp[i][j-1]
    return dp[-1][-1]
```
**Example (Edit Distance).**
```python
def edit(a, b):
    n, m = len(a), len(b)
    dp = [[0]*(m+1) for _ in range(n+1)]
    for i in range(n+1): dp[i][0] = i
    for j in range(m+1): dp[0][j] = j
    for i in range(1, n+1):
        for j in range(1, m+1):
            if a[i-1] == b[j-1]: dp[i][j] = dp[i-1][j-1]
            else: dp[i][j] = 1 + min(dp[i-1][j-1], dp[i-1][j], dp[i][j-1])
    return dp[n][m]
```
**Classic problems.** Unique Paths I/II, Min Path Sum, Edit Distance, Longest Common Subsequence, Maximal Square, Dungeon Game.
**Pitfall.** Off-by-one on boundaries; allocate `(n+1) × (m+1)` and treat row/col 0 as base case.
**Bridge → 3.4:** what if each item has a "weight"?

## 3.4 Knapsack family
**Mental model.** Pick items to maximize value subject to capacity. Two flavors:
- **0/1** — each item once. Inner loop *descending* on capacity.
- **Unbounded** — unlimited copies. Inner loop *ascending* on capacity.

**Example (0/1 Knapsack, 1D space).**
```python
def knapsack(W, items):
    dp = [0]*(W+1)
    for w, v in items:
        for c in range(W, w-1, -1):
            dp[c] = max(dp[c], dp[c-w] + v)
    return dp[W]
```
**Example (Coin Change unbounded — min coins).**
```python
def coin_change(coins, amt):
    INF = float('inf')
    dp = [0] + [INF]*amt
    for c in coins:
        for x in range(c, amt+1):
            dp[x] = min(dp[x], dp[x-c] + 1)
    return -1 if dp[amt] == INF else dp[amt]
```
**Classic problems.** 0/1 Knapsack, Partition Equal Subset Sum, Target Sum, Coin Change I/II, Last Stone Weight II.
**Pitfall.** Loop order swap (0/1 ↔ unbounded) is the most common bug.
**Bridge → 3.5:** what if intervals matter?

## 3.5 Interval DP
**Mental model.** State = `dp[l][r]` for the subproblem on `a[l..r]`. Transition: choose a split point `k` between `l` and `r`. `O(n³)` typical.

**Example (Matrix Chain / Burst Balloons).**
```python
def max_coins(a):
    a = [1] + a + [1]; n = len(a)
    dp = [[0]*n for _ in range(n)]
    for length in range(2, n):
        for l in range(n - length):
            r = l + length
            for k in range(l+1, r):
                dp[l][r] = max(dp[l][r], dp[l][k] + dp[k][r] + a[l]*a[k]*a[r])
    return dp[0][n-1]
```
**Classic problems.** Matrix Chain Multiplication, Burst Balloons, Stone Game, Strange Printer, Remove Boxes.
**Pitfall.** Iteration order — increasing length, then left endpoint.
**Bridge → 3.6:** what if the structure is a tree?

## 3.6 Tree DP
**Mental model.** Compute `f(u)` from `f(v)` for children. Process post-order. Often two values per node ("with u" / "without u").

**Example (House Robber III).**
```python
def rob_tree(root):
    def go(u):
        if not u: return (0, 0)
        L, R = go(u.left), go(u.right)
        take = u.val + L[1] + R[1]      # take u → cannot take children
        skip = max(L) + max(R)          # skip u → free to take or not
        return (take, skip)
    return max(go(root))
```
**Classic problems.** Diameter of Binary Tree, House Robber III, Binary Tree Cameras, Distribute Coins, Sum of Distances in Tree (rerooting).
**Pitfall.** *Rerooting* — when you need `f(v rooted at v)` for every `v`, do two DFS passes.
**Bridge → 3.7:** tree DP states are simple; sometimes you need *subset* states.

## 3.7 Bitmask DP
**Mental model.** Use a bitmask to encode which elements of a small set (≤ 20) have been used. State = `(mask, ...)`. `2ⁿ` states; transitions per state.

**Example (Travelling Salesman, n ≤ 20).**
```python
def tsp(dist):
    n = len(dist); INF = float('inf')
    dp = [[INF]*n for _ in range(1<<n)]
    dp[1][0] = 0
    for mask in range(1<<n):
        for u in range(n):
            if not (mask >> u) & 1: continue
            if dp[mask][u] == INF: continue
            for v in range(n):
                if (mask >> v) & 1: continue
                nm = mask | (1<<v)
                if dp[mask][u] + dist[u][v] < dp[nm][v]:
                    dp[nm][v] = dp[mask][u] + dist[u][v]
    return min(dp[(1<<n)-1][u] + dist[u][0] for u in range(n))
```
**Classic problems.** TSP, Partition to K Equal Sum Subsets, Min Cost to Connect, Smallest Sufficient Team, Beautiful Arrangement.
**Pitfall.** `n > 20` blows up. Submask enumeration uses `s = (s-1) & mask`.
**Bridge → 3.8:** all these were on graphs — let's get serious about shortest paths.

## 3.8 Dijkstra
**Mental model.** Single-source shortest path on **non-negative** weighted graph. Greedy: extract min-distance vertex, relax neighbors. With binary heap: `O((V + E) log V)`.

**Example (C++ — performance matters here).**
```cpp
#include <bits/stdc++.h>
using namespace std;
vector<long long> dijkstra(int n, vector<vector<pair<int,int>>>& g, int s) {
    const long long INF = 1e18;
    vector<long long> d(n, INF); d[s] = 0;
    priority_queue<pair<long long,int>, vector<pair<long long,int>>, greater<>> pq;
    pq.push({0, s});
    while (!pq.empty()) {
        auto [du, u] = pq.top(); pq.pop();
        if (du > d[u]) continue;
        for (auto [v, w] : g[u]) {
            if (d[u] + w < d[v]) { d[v] = d[u] + w; pq.push({d[v], v}); }
        }
    }
    return d;
}
```
**Classic problems.** Network Delay Time, Cheapest Flights with K Stops (modified state), Path with Minimum Effort, Swim in Rising Water, Minimum Cost to Make at Least One Path Valid (0-1 BFS).
**Pitfall.** Negative edges → wrong answer. Use Bellman–Ford (3.9). The "lazy delete" check `if du > d[u]: continue` is required for correctness with `priority_queue`.
**Bridge → 3.9:** what if edges *can* be negative?

## 3.9 Bellman–Ford & SPFA
**Mental model.** Relax every edge `V−1` times. `O(VE)`. Detects negative cycles via a V-th iteration that still relaxes.

**SPFA** = queue-based optimization; same worst case but often fast in practice. Susceptible to specially-crafted graphs.

**Example.**
```python
def bf(n, edges, s):
    INF = float('inf'); d = [INF]*n; d[s] = 0
    for _ in range(n - 1):
        for u, v, w in edges:
            if d[u] + w < d[v]: d[v] = d[u] + w
    # negative cycle?
    for u, v, w in edges:
        if d[u] + w < d[v]: return None
    return d
```
**Classic problems.** Detect Negative Cycle, Cheapest Flights with K Stops, Currency Arbitrage.
**Pitfall.** Don't use SPFA in problems where adversarial inputs are possible — it can degrade to `O(VE)`.
**Bridge → 3.10:** all-pairs shortest paths.

## 3.10 Floyd–Warshall
**Mental model.** `O(V³)` all-pairs shortest path via `d[i][j] = min(d[i][j], d[i][k] + d[k][j])`. Works with negative edges (no negative cycle).

**Example.**
```python
def fw(n, edges):
    INF = float('inf')
    d = [[INF]*n for _ in range(n)]
    for i in range(n): d[i][i] = 0
    for u, v, w in edges: d[u][v] = min(d[u][v], w)
    for k in range(n):
        for i in range(n):
            for j in range(n):
                if d[i][k] + d[k][j] < d[i][j]:
                    d[i][j] = d[i][k] + d[k][j]
    return d
```
**Classic problems.** All Pairs Shortest Path, Find the City With Smallest Number of Neighbors, Transitive Closure (boolean version).
**Pitfall.** Loop order matters — `k` outermost. Wrong order silently gives wrong answers.
**Bridge → 3.11:** shortest paths versus *spanning* trees.

## 3.11 MST: Kruskal & Prim
**Mental model.** Minimum-weight set of edges connecting all vertices. Two algorithms:
- **Kruskal** — sort edges, add if they don't create a cycle (DSU). `O(E log E)`.
- **Prim** — like Dijkstra: grow from a vertex; pick min-weight edge to outside. `O((V+E) log V)`.

**Example (Kruskal with DSU).**
```python
def kruskal(n, edges):
    edges.sort(key=lambda e: e[2])
    p = list(range(n))
    def find(x):
        while p[x] != x: p[x] = p[p[x]]; x = p[x]
        return x
    total = 0; used = 0
    for u, v, w in edges:
        ru, rv = find(u), find(v)
        if ru != rv: p[ru] = rv; total += w; used += 1
    return total if used == n - 1 else -1
```
**Classic problems.** Min Cost to Connect All Points, Connecting Cities With Minimum Cost, Optimize Water Distribution.
**Pitfall.** Forgetting to check connectivity (need exactly `n-1` edges).
**Bridge → 3.12:** range queries on arrays.

## 3.12 Segment tree (point update)
**Mental model.** Binary tree over array indices: each node stores the aggregate (sum/min/max/etc.) of a contiguous range. Update/query in `O(log n)`. Build `O(n)`.

**Example (sum, recursive).**
```python
class SegTree:
    def __init__(self, a):
        self.n = len(a); self.t = [0]*(4*self.n)
        self.build(1, 0, self.n-1, a)
    def build(self, node, l, r, a):
        if l == r: self.t[node] = a[l]; return
        m = (l+r)//2
        self.build(2*node, l, m, a); self.build(2*node+1, m+1, r, a)
        self.t[node] = self.t[2*node] + self.t[2*node+1]
    def update(self, node, l, r, i, v):
        if l == r: self.t[node] = v; return
        m = (l+r)//2
        if i <= m: self.update(2*node, l, m, i, v)
        else:      self.update(2*node+1, m+1, r, i, v)
        self.t[node] = self.t[2*node] + self.t[2*node+1]
    def query(self, node, l, r, ql, qr):
        if qr < l or r < ql: return 0
        if ql <= l and r <= qr: return self.t[node]
        m = (l+r)//2
        return self.query(2*node, l, m, ql, qr) + self.query(2*node+1, m+1, r, ql, qr)
```
**Classic problems.** Range Sum Query Mutable, Count Smaller After Self, Reverse Pairs, Range Min Query.
**Pitfall.** Allocate `4n` nodes, not `2n` (recursion-style needs the slack).
**Bridge → 3.13:** for *prefix* sums only, there's a simpler structure.

## 3.13 Fenwick / BIT
**Mental model.** Stores prefix aggregates implicitly via low-bit indexing. Sum/update in `O(log n)`. Half the constant factor of segment tree, but only for *prefix* queries.

**Example.**
```python
class BIT:
    def __init__(self, n): self.n = n; self.t = [0]*(n+1)
    def update(self, i, v):     # 1-indexed
        while i <= self.n: self.t[i] += v; i += i & -i
    def query(self, i):
        s = 0
        while i > 0: s += self.t[i]; i -= i & -i
        return s
    def range(self, l, r): return self.query(r) - self.query(l-1)
```
**Classic problems.** Count of Smaller Numbers After Self, Reverse Pairs, Number of Inversions.
**Pitfall.** 1-indexed. Forgetting offset is common.
**Bridge → 3.14:** range *updates*?

## 3.14 Lazy propagation
**Mental model.** Push pending updates lazily. When you visit a node fully covered by a range update, mark it lazy and stop. When you descend, push the lazy mark to children.

**When.** Range updates + range queries (sum/min/max).

**Sketch (range add, range sum).**
```cpp
struct SegTree {
    int n; vector<long long> t, lz;
    void apply(int node, int l, int r, long long v) {
        t[node] += v * (r - l + 1); lz[node] += v;
    }
    void push(int node, int l, int r) {
        if (lz[node]) {
            int m = (l + r) / 2;
            apply(2*node, l, m, lz[node]);
            apply(2*node+1, m+1, r, lz[node]);
            lz[node] = 0;
        }
    }
    void update(int node, int l, int r, int ql, int qr, long long v) {
        if (qr < l || r < ql) return;
        if (ql <= l && r <= qr) { apply(node, l, r, v); return; }
        push(node, l, r);
        int m = (l + r) / 2;
        update(2*node, l, m, ql, qr, v);
        update(2*node+1, m+1, r, ql, qr, v);
        t[node] = t[2*node] + t[2*node+1];
    }
};
```
**Classic problems.** Range Add Range Sum, Falling Squares, Painting the Wall, K-th Smallest in Range with Updates.
**Pitfall.** Forgetting to push before descending. Forgetting to combine lazy correctly when stacking updates.
**Bridge → 3.15:** strings, finally.

## 3.15 KMP
**Mental model.** Substring matching in `O(n + m)`. Precompute failure function (longest proper prefix that's also suffix) of pattern, then scan text without backtracking.

**Example (C++).**
```cpp
vector<int> failure(const string& p) {
    int m = p.size(); vector<int> f(m, 0);
    for (int i = 1, k = 0; i < m; ++i) {
        while (k > 0 && p[k] != p[i]) k = f[k-1];
        if (p[k] == p[i]) ++k;
        f[i] = k;
    }
    return f;
}
vector<int> kmp_search(const string& s, const string& p) {
    auto f = failure(p); vector<int> res;
    for (int i = 0, k = 0; i < (int)s.size(); ++i) {
        while (k > 0 && p[k] != s[i]) k = f[k-1];
        if (p[k] == s[i]) ++k;
        if (k == (int)p.size()) { res.push_back(i - k + 1); k = f[k-1]; }
    }
    return res;
}
```
**Classic problems.** Implement strStr, Shortest Palindrome, Repeated Substring Pattern, Longest Happy Prefix.
**Pitfall.** Off-by-one in failure indexing. Don't reinvent — use the template.
**Bridge → 3.16:** another linear-time variant.

## 3.16 Z-algorithm
**Mental model.** `Z[i]` = length of the longest substring starting at `i` that matches a prefix of `s`. `O(n)`. Substring search: build Z on `pattern + '$' + text`.

**Example.**
```python
def z_function(s):
    n = len(s); z = [0]*n; l = r = 0
    for i in range(1, n):
        if i < r: z[i] = min(r - i, z[i - l])
        while i + z[i] < n and s[z[i]] == s[i + z[i]]: z[i] += 1
        if i + z[i] > r: l, r = i, i + z[i]
    return z
```
**Classic problems.** Pattern Match (alternative to KMP), Palindromic Decomposition, String Matching with Wildcards.
**Pitfall.** Many implementations subtly differ — pick one.
**Bridge → 3.17:** what about hashing?

## 3.17 Rabin–Karp
**Mental model.** Polynomial rolling hash. Slide a window over the text and compare hashes; verify on collision. Average `O(n + m)`; worst `O(nm)` adversarially.

**Example.**
```python
def rabin_karp(s, p, MOD=(1<<61)-1, BASE=131):
    n, m = len(s), len(p)
    if m > n: return -1
    hp = 0; ht = 0; pw = 1
    for i in range(m):
        hp = (hp * BASE + ord(p[i])) % MOD
        ht = (ht * BASE + ord(s[i])) % MOD
        if i < m - 1: pw = pw * BASE % MOD
    if hp == ht and s[:m] == p: return 0
    for i in range(m, n):
        ht = ((ht - ord(s[i-m]) * pw) * BASE + ord(s[i])) % MOD
        if hp == ht and s[i-m+1:i+1] == p: return i - m + 1
    return -1
```
**Classic problems.** Find Common Substring, Repeated DNA Sequences, Longest Duplicate Substring (binary search on length + hashing).
**Pitfall.** Single-modulus collisions exist — for adversarial inputs use double hashing (two mods).
**Bridge → 3.18:** path-finding with heuristics.

## 3.18 A* search
**Mental model.** Like Dijkstra but uses `f(n) = g(n) + h(n)` where `h` is an *admissible* heuristic (never overestimates). Same correctness as Dijkstra when heuristic is admissible.

**When.** Pathfinding in grids, puzzle solvers (15-puzzle, sliding puzzle), planning. Don't use unless you have a real heuristic.

**Pitfall.** Inadmissible heuristic → wrong answer. Inconsistent heuristic → may need to re-expand nodes (or downgrade to Dijkstra).
**Bridge → Tier 4:** what does an expert toolbox look like?

---

# TIER 4 — Expert (rarely interviewed, often contest-decisive)

> Goals at this tier: recognize when these tools are **necessary** (not just applicable). Code by reference to a known-good template. Memorize complexity, not implementation lines.

## 4.1 Heavy–light decomposition (HLD)
**Idea.** Decompose tree into chains so that any root-to-leaf path crosses `O(log n)` chains. Each chain → segment tree → path queries in `O(log² n)`.
**When.** Path queries/updates on a tree (max edge, sum, etc.). `n ≤ 10⁵`.
**Pitfall.** Edge vs. vertex weights — different indexing. Use a known template (KACTL).
**Problem.** SPOJ QTREE, CF tree path problems.

## 4.2 Centroid decomposition
**Idea.** Recursively root the tree at its centroid. Build a hierarchy where any path is decomposed at some centroid. `O(n log n)` build.
**When.** Counting paths with property X (length ≤ K, length = K, etc.).
**Pitfall.** Inclusion–exclusion to avoid double-counting paths within the same subtree.
**Problem.** Count pairs of nodes within distance K; CF "Xenia and Tree."

## 4.3 Persistent segment tree
**Idea.** Each update creates a new version sharing unchanged nodes — tree of segment trees. Space `O((n + q) log n)`.
**When.** Offline queries on previous versions; k-th smallest in subarray; "wavelet tree alternative."
**Pitfall.** Memory pressure — pre-allocate; CP-Algorithms page is currently 404, prefer USACO Guide.
**Problem.** SPOJ MKTHNUM (k-th in range), Codeforces persistent counting problems.

## 4.4 Segment tree beats (Ji Driver Segment Tree)
**Idea.** Lazy with multiple tags: `chmin/chmax` plus sum. Amortized `O(n log² n)`.
**When.** Range chmin/chmax with sum/max queries.
**Pitfall.** Implementation is long and error-prone — use only when nothing simpler works.
**Problem.** HDU 5306 "Gorgeous Sequence."

## 4.5 Wavelet tree
**Idea.** Binary recursion over value bits with bit vectors at each level — answers k-th smallest, range count, range less-than in `O(log V)`.
**When.** Static array, lots of order-statistics queries.
**Alternative.** Persistent segment tree (4.3) is often simpler in CP.
**Problem.** SPOJ KQUERY.

## 4.6 Link–cut tree (Splay-based)
**Idea.** Dynamic forest with `link/cut/path-aggregate` in amortized `O(log n)`.
**When.** Online dynamic-connectivity / dynamic-MST. Rarely needed; offline approaches with DSU on rollback often suffice.
**Pitfall.** Splay tree subtle. Use a known template.
**Problem.** Codeforces "Dynamic MST"; SPOJ DYNACON1.

## 4.7 Suffix array + LCP (Kasai)
**Idea.** Sorted array of all suffixes; LCP array via Kasai's algorithm. Build `O(n log n)` (or `O(n log² n)` with sort). LCP enables substring counting, longest repeated substring, etc.
**When.** Multiple substring queries on a fixed string.
**Pitfall.** SA-IS gives `O(n)` but is rarely necessary.
**Problem.** SPOJ DISUBSTR (count distinct substrings).

## 4.8 Suffix automaton (SAM)
**Idea.** Smallest DFA accepting *all* substrings of a string. `O(n)` build with `len` and `link` arrays. Counts distinct substrings, finds longest common substring of two strings, etc.
**When.** You need distinct-substring stats or LCS of two strings in `O(n)`.
**Pitfall.** Reference implementations vary — pick one and stick to it (Um_nik blog 70018 has a clean version).
**Problem.** Distinct Substrings, LCS of two strings, Number of Occurrences.

## 4.9 Aho–Corasick
**Idea.** Trie + KMP-style failure links. Multi-pattern matching in `O(n + Σ |p_i|)`.
**When.** Many patterns scanned over a single text — virus scanners, DNA search.
**Pitfall.** Building "go" function with BFS over the trie.
**Problem.** Multi-pattern substring search; "censored words."

## 4.10 FFT / NTT
**Idea.** Multiply two polynomials in `O(n log n)`. NTT (Number Theoretic Transform) avoids floating-point error using a prime modulus.
**When.** Convolutions: number of ways to form sum, polynomial multiplication, big-integer multiplication.
**Pitfall.** Floating-point precision in FFT; modulus choice in NTT (998244353 is friendly).
**Problem.** Polynomial multiplication, count subsets with given sum (large ranges).

## 4.11 Min-cost max-flow (MCMF)
**Idea.** Send flow along shortest (by cost) augmenting paths — SPFA or Bellman–Ford for paths with negative edges (residuals).
**When.** Assignment problems, scheduling with costs, transportation.
**Pitfall.** Don't use MCMF when min-cut/Hungarian is enough. Use a known template (KACTL, e-maxx).
**Problem.** UVA 10806 "Dijkstra Dijkstra."

## 4.12 Hopcroft–Karp (bipartite matching)
**Idea.** Find augmenting paths via BFS layers, then DFS — `O(E √V)`.
**When.** Bipartite matching at scale.
**Pitfall.** Plain Hungarian-style DFS is `O(VE)` — usually fast enough; HK only when `V, E ~ 10⁵`.
**Problem.** Bipartite matching, vertex cover.

## 4.13 2-SAT
**Idea.** Boolean SAT with clauses of size 2. Reduce to implication graph; satisfiable iff no variable and its negation are in the same SCC. `O(V + E)` via Kosaraju/Tarjan.
**When.** "Either A or B is true" pairwise constraints.
**Pitfall.** Index gymnastics: variable `i` true → node `2i`; false → `2i+1`.
**Problem.** Codeforces "Yet Another 2-SAT" problems.

## 4.14 Convex hull trick / Li Chao tree
**Idea.** Maintain lower envelope of lines; query min/max at `x` in `O(log n)`. Li Chao = generic version on segment tree.
**When.** DP transition `dp[i] = min(dp[j] + a[j] * b[i] + c[i])` — linear in `b[i]`.
**Pitfall.** Lines must be monotone for the simple stack version; Li Chao works in general.
**Problem.** USACO Cuckoo Hashing, CF DP optimization tasks.

## 4.15 Digit DP
**Idea.** DP over digits of a number with state `(position, tight, leading_zero, ...)`.
**When.** Count integers ≤ N with property X.
**Pitfall.** `tight` flag must propagate carefully; treat leading zero separately.
**Problem.** Count numbers with no two consecutive equal digits; CSES Counting Numbers.

## 4.16 DP on broken profile (broken contour)
**Idea.** State = bitmask of one row's column "profile" being filled. Transition fills cells column by column.
**When.** Tile a grid `n × m` with dominoes/L-trominoes (`m ≤ ~15`).
**Pitfall.** The transition table is the whole problem — generate it with bit DP carefully.
**Problem.** SPOJ "GNY07H," domino tilings.

## 4.17 Mo's algorithm (with updates)
**Idea.** Offline range queries; sort queries by `(block of L, R)`. Each query `O(√n)` amortized.
**With updates** — three-dimensional sort `(L block, R block, time)` → `O(n^{5/3})`.
**When.** Offline range mode/distinct-count queries.
**Pitfall.** Block size √n is non-negotiable; tune for the specific problem.
**Problem.** SPOJ DQUERY (distinct elements in range).

## 4.18 LCA: binary lifting & Euler tour
**Idea.**
- **Binary lifting** — precompute `up[u][k] = (2ᵏ-th ancestor of u)`. LCA in `O(log n)` per query, `O(n log n)` build.
- **Euler tour + RMQ** — flatten tree; LCA = min depth in range. With sparse table, `O(1)` query.
**When.** Many tree distance / LCA queries.
**Pitfall.** Off-by-one when lifting; handle `depth(u) ≠ depth(v)` first.
**Problem.** Tree distance queries; competitive HLD prerequisite.

## 4.19 Sprague–Grundy / game theory
**Idea.** Every impartial game has a *Grundy number* `g(s) = mex{g(s') : s → s'}`. Sum of independent games = XOR of Grundy numbers; first player loses iff XOR is 0.
**When.** "Take-away" games, Nim variants, decomposable game positions.
**Pitfall.** Only impartial games. Partizan games (chess) are out of scope.
**Problem.** Nim, Staircase Nim, "Game on tree."

## 4.20 Randomized algorithms
**Three patterns:**
- **Hashing with random base/mod** — defends against adversarial collision attacks.
- **Treap / random BST** — amortized balanced BST without complex rotations.
- **Reservoir sampling** — uniform sample of stream of unknown length: keep i-th element with prob `1/i`.

**Example (reservoir sampling).**
```python
import random
def reservoir(stream, k=1):
    res = []
    for i, x in enumerate(stream):
        if i < k: res.append(x)
        elif random.random() < k / (i + 1):
            res[random.randrange(k)] = x
    return res
```
**Problems.** Linked List Random Node, Random Pick with Weight; CF problems requiring randomization to avoid worst-case hash collision.
**Pitfall.** *Cryptographic* randomness vs. PRNG — most CP problems require neither, but use random seed not 0.

---

# META — Cross-Cutting Problem-Solving Skills

## M.1 How to read a problem
**Routine.**
1. Read once for *meaning*.
2. Read again writing down: input, output, constraints, examples by hand.
3. Restate the problem in one sentence — if you can't, you don't understand it.
4. Look at the smallest test case and *trace* the expected output.
5. Look at the largest constraints — they tell you the target complexity (M.2).

**Pitfall.** Skipping examples is the #1 cause of wrong solutions. Compute by hand for `n = 1, 2, 3` *before* coding.

## M.2 Constraints → algorithm cheat sheet
Use the limit on `n` to back into algorithmic budget (1 sec ≈ 10⁸ simple ops):

| n | Budget | Likely approaches |
|---|--------|-------------------|
| ≤ 11 | n! | brute permutations |
| ≤ 20 | 2ⁿ | bitmask DP, meet-in-the-middle |
| ≤ 100 | n³, n² log n | Floyd–Warshall, interval DP |
| ≤ 5,000 | n² | knapsack, DP, classic 2D |
| ≤ 10⁵ | n log n, n √n | sort, segment tree, Mo's |
| ≤ 10⁶ | n, n log n | linear scans, sieve |
| ≤ 10⁹ | log n | binary search, math |

**The mental move:** "constraints first" → trims your candidate algorithms before you waste time.

## M.3 Always brute force first
Code the brute force, even if `O(n^4)`. Why?
1. **Correctness reference** — stress test (M.7) the optimized solution against it.
2. **Reveals structure** — patterns, monotonicity, redundant work.
3. **Partial credit** — many problems have subtasks where brute force passes.

**Move:** never optimize a wrong solution.

## M.4 The 14 FAANG patterns
Most LeetCode mediums collapse to one of:

1. Two pointers
2. Sliding window
3. Fast & slow pointers
4. Merge intervals
5. In-place reversal
6. Cyclic sort
7. BFS / DFS on tree-graph
8. Topological sort
9. K-way merge
10. Top-k via heap
11. Subsets / backtracking
12. 0/1 knapsack DP
13. Unbounded knapsack DP
14. LIS / LCS-style DP

When you read a problem, ask: "which of these 14 fits?" If none — read again.

## M.5 Invariants & monovariants
**Invariant** — a property unchanged by every operation. **Monovariant** — a quantity that strictly increases or decreases.

**Examples.**
- Each turn parity flips → if you swap two adjacent elements, parity of inversion count flips. (15-puzzle solvability.)
- Sum of array constant under "add 1 to one, subtract 1 from another."
- Heap operations preserve heap property (invariant).

**Move:** ask "what doesn't change?" → it constrains the answer.

## M.6 Reductions
Map problem A to problem B you already know. Reduction = new problem becomes old problem in disguise.

**Examples.**
- "Find duplicate in array of 1..n" → cycle detection in linked list (Floyd's).
- "Course schedule" → topo sort on dependency graph.
- "Word ladder" → BFS shortest path on string-similarity graph.
- "K-th largest in stream" → min-heap of size K.

If you don't recognize a problem, ask: "what does this look like *almost*?"

## M.7 Stress testing
**Recipe** for any problem you submit:
1. Write **brute** — slow but obviously correct.
2. Write **fast** — your candidate solution.
3. Write **gen** — random small test generator.
4. Loop: generate, run both, diff outputs. Found a difference → minimize the test case manually.

Even 5 minutes of stress testing catches more bugs than 30 minutes of staring.

```python
# pseudocode
while True:
    test = gen()
    if brute(test) != fast(test):
        print("MISMATCH", test); break
```

## M.8 DP state design
**Method.**
1. What does the problem ask at the *end*? That's the answer state.
2. What decisions remain at any moment? That's the state's "future."
3. What information from the past affects future decisions? That's the state's "memory."
4. Strip redundant memory — collapse symmetries.

**Example.** *"Paint houses, no two adjacent same color."* State: `(i, last_color)`. Memory of *which* houses came before is irrelevant — only the last color affects future.

**Pitfall.** State explosion = your state has too much memory. Ask "what's the minimum I need to remember?"

## M.9 Time–space tradeoffs
- Memoization buys time with space.
- Rolling DP (1D out of 2D) buys back space.
- Sparse representations save space when data is sparse.
- Bitsets are 64× faster than `bool` arrays for boolean DP.

**Move:** when stuck on TLE, look for repeated computation. When stuck on MLE, look for redundant state.

## M.10 Brute / Better / Best framework
Always present three solutions in interviews:
- **Brute** — naive, obviously correct, with complexity.
- **Better** — one optimization step (e.g., hashmap, sort, monotone trick).
- **Best** — final solution at target complexity.

Forces you to *think in steps*, lets the interviewer follow, and shows you can iterate.

## M.11 Mock interviews
Mocks force the *speaking* skill that solo practice doesn't. Cadence:
1. **Restate** the problem.
2. **Walk through** a small example.
3. **Propose brute** + complexity.
4. **Propose better** with the optimization insight.
5. **Code** with running commentary.
6. **Test** with edge cases (empty, single, duplicates, max size).

Pirateinterviews, Pramp, Interviewing.io, peers — pick one. Do at least 5 before a real interview.

## M.12 Deliberate practice
Untimed solving = comfort zone. Real growth requires *targeted* discomfort.

**Routine (per day).**
- 1 problem at your *current* level (build confidence).
- 1 problem one level above (stretch).
- 30 min reviewing a *failed* problem from last week — re-solve from scratch, then read editorial.

Volume without review = wasted reps.

## M.13 Climbing ratings
- Codeforces 1200 → 1600: master Tier 1–2.
- 1600 → 1900: master Tier 3 + Meta.
- 1900 → 2200: master Tier 4 partially; learn 2 new techniques per month.
- 2200+: speed and accuracy, not new topics.

The bottleneck shifts: at low ratings it's *knowledge*; at high ratings it's *implementation speed and bug-free coding*.

## M.14 Reading editorials
**Method.**
1. Try the problem cold for 30–60 min.
2. Read editorial *until* the key idea clicks. Stop.
3. Code the rest yourself.
4. If you couldn't have invented the trick: write it on a notecard, "next time I see X, try Y."

Reading editorials *before* trying = reading-comprehension exercise, not problem-solving.

---

# Practice Plan

## 4-week sprint (zero → solid intermediate)

**Week 1.** Tier 1 + M.1, M.2, M.3. 3 problems/day from NeetCode 150's "easy" tier.
**Week 2.** Tier 2 (graphs, heaps) + M.4. 3 problems/day, add one medium.
**Week 3.** Tier 2 finish + M.5, M.7, M.8. 2 mediums/day. Stress-test every solution.
**Week 4.** Tier 3 (DP basics) + M.10. 1 medium and 1 hard/day.

By end of Week 4 you should pass most LeetCode mediums in 25 minutes.

## 3-month plan (intermediate → advanced)
- Month 1: Tier 3 in full + AtCoder EDPC contest (26 DP problems).
- Month 2: Tier 3 advanced (segment tree, KMP) + start Codeforces virtual contests.
- Month 3: Begin Tier 4 selectively (HLD, persistent segtree, FFT) based on the contests you do.

## 6+ month plan (advanced → expert)
- Solve CSES Problem Set (300 curated problems).
- Contest weekly — Codeforces Round, AtCoder Beginner / Regular Contest.
- Learn 1 Tier-4 topic per 2 weeks. Implement template, solve 3 problems.

---

# Resources

**Free curricula.**
- [USACO Guide](https://usaco.guide/) — best free structured curriculum, Bronze→Platinum.
- [CP-Algorithms](https://cp-algorithms.com/) — encyclopedic, with code.
- [NeetCode 150](https://neetcode.io/) — best for FAANG interview prep.
- [AtCoder EDPC](https://atcoder.jp/contests/dp) — 26 DP problems, increasing difficulty.
- [CSES Problem Set](https://cses.fi/problemset/) — 300 curated problems with editorials.
- [Codeforces EDU](https://codeforces.com/edu/courses) — interactive courses on segment trees, DSU, etc.

**Books.**
- *Cracking the Coding Interview* (McDowell) — interview baseline.
- *Competitive Programming 4* (Halim, Halim) — encyclopedic.
- *The Algorithm Design Manual* (Skiena) — for understanding *why*.
- *CLRS* — reference, not first-read.

**Templates & references.**
- [KACTL](https://github.com/kth-competitive-programming/kactl) — KTH's competitive programming reference.
- Errichto's YouTube channel — segment tree, DP, contest walkthroughs.
- Um_nik's Codeforces blogs (62730, 21344, 57216, 20548, 70018) — expert insights.

---

# Footnotes & Confidence

- All code samples were written with reference to standard implementations from KACTL, CP-Algorithms, USACO Guide, and standard CS textbooks. Test before relying in contest.
- A few Tier-4 references in the source research had broken URLs (CP-Algorithms 404s on digit-dp, CHT, persistent-segtree pages at the time of research) — fall back to USACO Guide or KACTL when those are down.
- This document is a *map*, not a substitute for code-by-hand. The table of contents is 77 items but the journey is **77 problems × 3 attempts each ≈ 231 sittings**. Plan accordingly.

---

## You don't have a knowledge problem. You have a follow-through problem.

You now have 77 topics, examples, problems, and a plan. The bookshelf is full. So was it last time. The question isn't *which topic should I study next?* — that's a procrastination dressed up as planning.

**The uncomfortable question:**

Pick **exactly one** to commit to publicly (tell a friend, a Discord, a colleague — anyone) by the end of today:

1. I will solve the example problem from **3 specific topics in this document** by next Sunday — and I'll send the code to ___________.
2. I will do a **weekly contest on Codeforces / LeetCode** for 4 consecutive weeks starting this week, and I'll publish my rating after each.
3. I will run **5 stress tests (M.7) on every "fast" solution** I write for the next 30 days, no exceptions.
4. None of the above — which is your honest answer that this curriculum will join the pile of bookmarked tabs you'll never re-open.

Pick one. Or admit option 4. Either way, stop reading this and go.
