# Question D Explanation

## Key observation

For a fixed root `r`, a node `u` can appear as the LCA of some set of `k` distinct nodes **iff** the subtree of `u` (when the tree is rooted at `r`) contains at least `k` nodes.

- If `u` is the LCA of a chosen set of `k` nodes, then all of them must lie inside the subtree of `u`, so `subtree_r(u) >= k`.
- If `subtree_r(u) >= k`, we can choose `u` itself and any other `k-1` nodes inside its subtree. Then their LCA is exactly `u`.

So for each root `r`, the value `f(r)` is simply the number of nodes whose rooted subtree size is at least `k`.

## Re-rooting interpretation

Now fix a node `u` and ask: for how many roots `r` does `subtree_r(u) >= k` hold?

If we remove node `u`, the tree splits into several connected components.
If the root `r` lies in a component of size `c`, then the subtree of `u` under root `r` has size:

`subtree_r(u) = n - c`

Therefore, `u` is valid for that root iff:

`n - c >= k`
`c <= n - k`

So the number of valid roots for node `u` is:

`1 + sum of sizes of all components after removing u whose size <= n-k`

The `+1` corresponds to the case `r = u`.

## Implementation

I root the tree arbitrarily at node `1` and compute subtree sizes `sz[u]`.

For every node `u`, the component sizes after removing `u` are:
- `sz[v]` for every child `v` of `u`
- `n - sz[u]` for the parent side (if it exists)

Then I sum all component sizes `c` such that `c <= n-k`, and add `1` for `r = u`.

This gives an `O(n)` solution per test case.