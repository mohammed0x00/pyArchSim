class Cache:
    def __init__(s, port_id, cache_size_kb=2, cacheline_size=16, associativity=1):
        s.port_id = port_id
        s.cache_size = cache_size_kb * 1024  # Convert KB to Bytes
        s.cacheline_size = cacheline_size
        s.associativity = associativity
        s.num_sets = cache_size_kb // (cacheline_size * associativity)
        s.tags = [[] for _ in range(s.num_sets)]
        s.data = [[] for _ in range(s.num_sets)]
        s.repl_ptr = [0 for _ in range(s.num_sets)]
        s.pending = None
        s.delay = 0

        # Additional tracking for line trace
        s.last_access_was_miss = False
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
        if s.pending is not None:
            raise Exception("Blocking cache still busy")
        s.pending = req
        s.last_access_was_miss = not s.isHit(req['addr'])
        s.just_missed = s.last_access_was_miss
        s.just_sent_this_cycle = True
        s.delay = 1 if not s.last_access_was_miss else 10
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

    def linetrace(s):
        if not s.active:
            return "idle"
        if s.pending:
            if s.just_sent_this_cycle and s.just_missed:
                return "MISS"
            elif s.delay > 0:
                return "WAIT"
            elif s.isHit(s.pending['addr']):
                return "HIT"
            else:
                return "MISS"
        return "idle"

    def isHit(s, addr):
        tag = addr // s.cacheline_size
        index = (addr // s.cacheline_size) % s.num_sets
        return tag in s.tags[index]

    def processReq(s, req):
        addr = req['addr']
        tag = addr // s.cacheline_size
        index = (addr // s.cacheline_size) % s.num_sets
        block_offset = addr % s.cacheline_size

        if tag in s.tags[index]:
            block_idx = s.tags[index].index(tag)
            data_block = s.data[index][block_idx]
            data = data_block[block_offset:block_offset + req['size']]
        else:
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
                    if len(s.tags[index]) >= s.associativity:
                        s.tags[index].pop(0)
                        s.data[index].pop(0)
                    s.tags[index].append(tag)
                    s.data[index].append(new_block)
                    data = new_block[block_offset:block_offset + req['size']]
                else:
                    return None
            else:
                return None

        return {
            'op': req['op'],
            'addr': req['addr'],
            'data': data,
            'size': req['size'],
            'mask': req['mask'],
            'tag': req['tag']
        }
