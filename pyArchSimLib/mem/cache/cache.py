# cache.py
# --------------------------------------------------------------------
# A set-associative cache class it also can act as a direct/fully-associative cache.
#
# Author\ Mohammed Mansour
# Date  \ 23 May 2025

class CacheLine:
    def __init__(self, tag=None, data=None, valid=False):
        self.tag = tag
        self.data = data if data is not None else []
        self.valid = valid

class Cache:
    def __init__(s, port_id, cache_size_kb=1, cacheline_size=16, associativity=1):
        s.port_id = port_id
        s.cache_size = cache_size_kb * 1024  # Convert KB to Bytes
        s.cacheline_size = cacheline_size
        s.associativity = associativity
        s.num_sets = s.cache_size // (cacheline_size * associativity)
        
        # Each set is a list of CacheLine objects
        s.sets = [[] for _ in range(s.num_sets)]
        s.pending = None
        s.delay = 0

        # Additional information
        s.just_sent_this_cycle = False
        s.just_missed = False
        s.active = False

    # Connections
    def setMemCanReq(s, MemCanReq):
        s.MemCanReq   = MemCanReq
    def setMemSendReq(s, MemSendReq):
        s.MemSendReq  = MemSendReq
    def setMemHasResp(s, MemHasResp):
        s.MemHasResp  = MemHasResp
    def setMemRecvResp(s, MemRecvResp):
        s.MemRecvResp = MemRecvResp

    def canReq(s):
        return s.pending is None

    def sendReq(s, req):
        if s.canReq() is not True:
            raise Exception("Cache is busy, cannot send new request")
        s.pending = req
        s.just_missed = not s.isHit(req['addr'])
        s.just_sent_this_cycle = True
        s.delay = 1
        s.active = True

    def hasResp(s):
        return s.pending is not None and s.delay == 0 and s.processReq(s.pending) is not None

    def recvResp(s):
        if s.pending is None:
            return None
        resp = s.processReq(s.pending)
        if resp is None:
            return None
        s.pending = None
        s.active = False
        return resp

    def tick(s):
        if s.pending and s.delay > 0:
            s.delay -= 1
        s.just_sent_this_cycle = False
        if s.pending is None:
            s.active = False
            
    def isHit(s, addr):
        tag = addr // s.cacheline_size
        index = (addr // s.cacheline_size) % s.num_sets
        for line in s.sets[index]:
            if line.valid and line.tag == tag:
                return True
        return False

    def processReq(s, req):
        addr = req['addr']
        tag = addr // s.cacheline_size
        index = (addr // s.cacheline_size) % s.num_sets
        block_offset = addr % s.cacheline_size

        # Search for hit
        for i, line in enumerate(s.sets[index]):
            if line.valid and line.tag == tag:
                data = line.data[block_offset:block_offset + req['size']]
                # Move to MRU (end of list) for LRU
                s.sets[index].append(s.sets[index].pop(i))
                return {
                    'op': req['op'],
                    'addr': req['addr'],
                    'data': data,
                    'size': req['size'],
                    'mask': req['mask'],
                    'tag': req['tag']
                }

        # Miss: fetch from memory
        mem_req = {
            'op': 0,
            'addr': addr - block_offset,
            'size': s.cacheline_size,
            'data': [],
            'mask': None,
            'tag': None
        }
        if s.MemCanReq(s.port_id):
            s.MemSendReq(s.port_id, mem_req)
            if s.MemHasResp(s.port_id):
                mem_resp = s.MemRecvResp(s.port_id)
                new_block = mem_resp['data']
                # Evict if needed
                if len(s.sets[index]) >= s.associativity:
                    s.sets[index].pop(0)
                # Insert new line as MRU
                new_line = CacheLine(tag=tag, data=new_block, valid=True)
                s.sets[index].append(new_line)
                data = new_block[block_offset:block_offset + req['size']]
                return {
                    'op': req['op'],
                    'addr': req['addr'],
                    'data': data,
                    'size': req['size'],
                    'mask': req['mask'],
                    'tag': req['tag']
                }
            else:
                return None
        else:
            return None
        
    def linetrace(s):
        if not s.active:
            value = " -- "
        elif s.pending:
            if s.just_sent_this_cycle and s.just_missed:
                value = "miss"
            elif s.delay > 0:
                value = "wait"
            elif s.isHit(s.pending['addr']):
                value = "hit "
            else:
                value = "miss"
        else:
            value = " -- "
        return 2 * ' ' + value + ' '