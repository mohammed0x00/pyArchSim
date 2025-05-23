# five_stage_proc.py
# --------------------------------------------------------------------
# Simple five-stage pipelined processor.
#
# Author\ Khalid Al-Hawaj
# Date  \ 5 May 2025

import random

from pyArchSimLib.proc.core import FiveStageInorderCore
from pyArchSimLib.mem.cache import Cache, NoCache

class FiveStageInorderProcessor():
  def __init__(s):
    # Core
    s.core = FiveStageInorderCore()

    # Caches
    s.icache = Cache(0)
    s.dcache = Cache(1)

    # Memory interface for syscalls
    s.MemReadFunct  = None
    s.MemWriteFunct = None

    # Connect
    ## imem
    s.core.setIMemCanReq  (s.icache.canReq  )
    s.core.setIMemSendReq (s.icache.sendReq )
    s.core.setIMemHasResp (s.icache.hasResp )
    s.core.setIMemRecvResp(s.icache.recvResp)
    ## dmem
    s.core.setDMemCanReq  (s.dcache.canReq  )
    s.core.setDMemSendReq (s.dcache.sendReq )
    s.core.setDMemHasResp (s.dcache.hasResp )
    s.core.setDMemRecvResp(s.dcache.recvResp)

  # Connections
  def setMemReadFunct(s, MemReadFunct):
    s.MemReadFunct  = MemReadFunct
    s.core.setMemReadFunct(MemReadFunct)

  def setMemWriteFunct(s, MemWriteFunct):
    s.MemWriteFunct = MemWriteFunct
    s.core.setMemWriteFunct(MemWriteFunct)

  # Connections
  def setMemCanReq(s, MemCanReq):
    s.MemCanReq   = MemCanReq
    s.icache.setMemCanReq(MemCanReq)
    s.dcache.setMemCanReq(MemCanReq)
  def setMemSendReq(s, MemSendReq):
    s.MemSendReq  = MemSendReq
    s.icache.setMemSendReq(MemSendReq)
    s.dcache.setMemSendReq(MemSendReq)
  def setMemHasResp(s, MemHasResp):
    s.MemHasResp  = MemHasResp
    s.icache.setMemHasResp(MemHasResp)
    s.dcache.setMemHasResp(MemHasResp)
  def setMemRecvResp(s, MemRecvResp):
    s.MemRecvResp = MemRecvResp
    s.icache.setMemRecvResp(MemRecvResp)
    s.dcache.setMemRecvResp(MemRecvResp)

  # Flags
  def roiFlag(s):
    return s.core.roiFlag()
  def instCompletionFlag(s):
    return s.core.instCompletionFlag()

  # Exit
  def getExitStatus(s):
    return s.core.getExitStatus()

  # Tick
  def tick(s):
    s.core.tick()
    s.icache.tick()
    s.dcache.tick()

  def linetrace(s):
    core_lt   = s.core.linetrace()
    icache_lt = s.icache.linetrace()
    dcache_lt = s.dcache.linetrace()

    lt_buf = core_lt
    if icache_lt != '': lt_buf += ' | ' + icache_lt
    if dcache_lt != '': lt_buf += ' | ' + dcache_lt

    return lt_buf
