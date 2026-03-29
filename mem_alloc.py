#!/usr/bin/env python3
"""Memory allocation — First Fit, Best Fit, Worst Fit, Buddy."""
import sys

class MemoryAllocator:
    def __init__(self, size):
        self.size = size
        self.free = [(0, size)]
        self.allocated = {}
    def _alloc(self, name, size, strategy="first"):
        candidates = [(s, e) for s, e in self.free if e - s >= size]
        if not candidates: return False
        if strategy == "first": block = candidates[0]
        elif strategy == "best": block = min(candidates, key=lambda b: b[1]-b[0])
        elif strategy == "worst": block = max(candidates, key=lambda b: b[1]-b[0])
        else: block = candidates[0]
        s, e = block
        self.free.remove(block)
        if e - s > size: self.free.append((s + size, e))
        self.free.sort()
        self.allocated[name] = (s, s + size)
        return True
    def free_block(self, name):
        if name not in self.allocated: return False
        s, e = self.allocated.pop(name)
        self.free.append((s, e))
        self.free.sort()
        self._coalesce()
        return True
    def _coalesce(self):
        merged = []
        for s, e in self.free:
            if merged and merged[-1][1] >= s:
                merged[-1] = (merged[-1][0], max(merged[-1][1], e))
            else:
                merged.append((s, e))
        self.free = merged
    def show(self):
        print(f"  Allocated: {self.allocated}")
        print(f"  Free: {self.free}")

if __name__ == "__main__":
    size = int(sys.argv[1]) if len(sys.argv) > 1 else 1024
    for strategy in ["first", "best", "worst"]:
        print(f"\n=== {strategy.upper()} FIT (memory={size}) ===")
        ma = MemoryAllocator(size)
        for name, sz in [("A", 200), ("B", 350), ("C", 100), ("D", 250)]:
            ok = ma._alloc(name, sz, strategy)
            print(f"  Alloc {name}({sz}): {'OK' if ok else 'FAIL'}")
        ma.show()
        ma.free_block("B")
        print("  Free B:")
        ma._alloc("E", 150, strategy)
        print(f"  Alloc E(150):")
        ma.show()
