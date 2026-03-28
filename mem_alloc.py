#!/usr/bin/env python3
"""mem_alloc - Memory allocator simulation (first-fit, best-fit, buddy)."""
import sys
class MemoryAllocator:
    def __init__(s,size):s.size=size;s.blocks=[(0,size,True)]
    def alloc(s,size,strategy="first_fit"):
        if strategy=="first_fit":idx=next((i for i,(start,sz,free) in enumerate(s.blocks) if free and sz>=size),None)
        elif strategy=="best_fit":
            candidates=[(i,sz) for i,(start,sz,free) in enumerate(s.blocks) if free and sz>=size]
            idx=min(candidates,key=lambda x:x[1])[0] if candidates else None
        elif strategy=="worst_fit":
            candidates=[(i,sz) for i,(start,sz,free) in enumerate(s.blocks) if free and sz>=size]
            idx=max(candidates,key=lambda x:x[1])[0] if candidates else None
        if idx is None:return None
        start,sz,_=s.blocks[idx]
        if sz>size:s.blocks[idx]=(start,size,False);s.blocks.insert(idx+1,(start+size,sz-size,True))
        else:s.blocks[idx]=(start,sz,False)
        return start
    def free(s,addr):
        for i,(start,sz,free) in enumerate(s.blocks):
            if start==addr and not free:s.blocks[i]=(start,sz,True);s._coalesce();return True
        return False
    def _coalesce(s):
        merged=[]
        for start,sz,free in s.blocks:
            if merged and merged[-1][2] and free:merged[-1]=(merged[-1][0],merged[-1][1]+sz,True)
            else:merged.append((start,sz,free))
        s.blocks=merged
    def __repr__(s):
        parts=[]
        for start,sz,free in s.blocks:parts.append(f"[{start}:{start+sz}]{'free' if free else 'used'}")
        return" ".join(parts)
if __name__=="__main__":
    mem=MemoryAllocator(100);print(f"Initial: {mem}")
    a1=mem.alloc(20);a2=mem.alloc(30);a3=mem.alloc(15);print(f"After allocs: {mem}")
    mem.free(a1);print(f"After free({a1}): {mem}")
    a4=mem.alloc(10);print(f"After alloc(10): {mem}")
    mem.free(a2);mem.free(a3);print(f"After freeing all: {mem}")
