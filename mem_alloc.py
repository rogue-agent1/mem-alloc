#!/usr/bin/env python3
"""mem_alloc: Memory allocator simulation (first-fit, best-fit, buddy)."""
import sys

class FirstFit:
    def __init__(self, size):
        self.size = size
        self.free = [(0, size)]  # (start, length)
        self.allocated = {}  # id -> (start, length)
        self._id = 0

    def alloc(self, n):
        for i, (start, length) in enumerate(self.free):
            if length >= n:
                self._id += 1
                self.allocated[self._id] = (start, n)
                if length == n:
                    self.free.pop(i)
                else:
                    self.free[i] = (start + n, length - n)
                return self._id
        return None

    def free_block(self, block_id):
        if block_id not in self.allocated: return False
        start, n = self.allocated.pop(block_id)
        self.free.append((start, n))
        self.free.sort()
        self._coalesce()
        return True

    def _coalesce(self):
        merged = []
        for start, length in self.free:
            if merged and merged[-1][0] + merged[-1][1] == start:
                merged[-1] = (merged[-1][0], merged[-1][1] + length)
            else:
                merged.append((start, length))
        self.free = merged

    def fragmentation(self):
        total_free = sum(l for _, l in self.free)
        max_free = max((l for _, l in self.free), default=0)
        if total_free == 0: return 0
        return 1 - max_free / total_free

class BestFit(FirstFit):
    def alloc(self, n):
        best_idx = None
        best_size = float('inf')
        for i, (start, length) in enumerate(self.free):
            if length >= n and length < best_size:
                best_idx = i
                best_size = length
        if best_idx is None: return None
        start, length = self.free[best_idx]
        self._id += 1
        self.allocated[self._id] = (start, n)
        if length == n:
            self.free.pop(best_idx)
        else:
            self.free[best_idx] = (start + n, length - n)
        return self._id

class BuddyAllocator:
    def __init__(self, order):
        self.order = order
        self.size = 1 << order
        self.free = {i: [] for i in range(order + 1)}
        self.free[order] = [0]
        self.allocated = {}
        self._id = 0

    def _order_for(self, n):
        o = 0
        while (1 << o) < n: o += 1
        return o

    def alloc(self, n):
        needed = self._order_for(n)
        for o in range(needed, self.order + 1):
            if self.free[o]:
                addr = self.free[o].pop(0)
                while o > needed:
                    o -= 1
                    buddy = addr + (1 << o)
                    self.free[o].append(buddy)
                self._id += 1
                self.allocated[self._id] = (addr, needed)
                return self._id
        return None

    def free_block(self, block_id):
        if block_id not in self.allocated: return False
        addr, order = self.allocated.pop(block_id)
        while order < self.order:
            buddy = addr ^ (1 << order)
            if buddy in self.free[order]:
                self.free[order].remove(buddy)
                addr = min(addr, buddy)
                order += 1
            else:
                break
        self.free[order].append(addr)
        self.free[order].sort()
        return True

def test():
    # First fit
    ff = FirstFit(100)
    a = ff.alloc(30)
    b = ff.alloc(20)
    c = ff.alloc(50)
    assert a and b and c
    assert ff.alloc(1) is None  # Full
    ff.free_block(b)
    d = ff.alloc(15)
    assert d  # Fits in freed slot
    # Best fit
    bf = BestFit(100)
    bf.alloc(30)
    bf.alloc(20)
    bf.free_block(1)  # Free 30-block
    e = bf.alloc(10)
    assert e  # Should fit in 30-block (best fit)
    # Buddy
    buddy = BuddyAllocator(4)  # 16 bytes
    x = buddy.alloc(3)  # Needs order 2 (4 bytes)
    y = buddy.alloc(3)
    assert x and y
    buddy.free_block(x)
    buddy.free_block(y)
    # Should coalesce back
    z = buddy.alloc(16)
    assert z  # Full block available again
    # Fragmentation
    ff2 = FirstFit(100)
    ff2.alloc(10)
    ff2.alloc(10)
    ff2.alloc(10)
    ff2.free_block(2)  # Free middle
    assert ff2.fragmentation() > 0
    print("All tests passed!")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "test": test()
    else: print("Usage: mem_alloc.py test")
