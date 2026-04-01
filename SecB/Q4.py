import sys

input = sys.stdin.readline


def solve():
    t = int(input())
    out = []

    for _ in range(t):
        n, k = map(int, input().split())
        g = [[] for _ in range(n + 1)]

        for _ in range(n - 1):
            u, v = map(int, input().split())
            g[u].append(v)
            g[v].append(u)

        # 1) iterative DFS: build parent[] and traversal order
        parent = [0] * (n + 1)
        order = [1]
        parent[1] = -1

        for u in order:
            for v in g[u]:
                if v == parent[u]:
                    continue
                parent[v] = u
                order.append(v)

        # 2) subtree sizes
        sz = [1] * (n + 1)
        for u in reversed(order):
            for v in g[u]:
                if v == parent[u]:
                    continue
                sz[u] += sz[v]

        # 3) count contribution of each node u
        # A root r is valid for u iff the component containing r
        # after removing u has size c <= n-k
        limit = n - k
        ans = 0

        for u in range(1, n + 1):
            contrib = 1  # root = u is always valid

            for v in g[u]:
                if parent[v] == u:
                    # child-side component
                    c = sz[v]
                else:
                    # parent-side component
                    c = n - sz[u]

                if c <= limit:
                    contrib += c

            ans += contrib

        out.append(str(ans))

    print("\n".join(out))


if __name__ == "__main__":
    solve()