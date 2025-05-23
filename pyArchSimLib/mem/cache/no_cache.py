# no_cache.py
# --------------------------------------------------------------------
# A no cache to act as a passthru.
#
# Author\ Khalid Al-Hawaj
# Date  \ 10 May 2025

import random

class NoCache():
  def __init__(s, port_id):
    s.port_id = port_id

  # Connections
  def setMemCanReq(s, MemCanReq):
    s.MemCanReq   = MemCanReq
  def setMemSendReq(s, MemSendReq):
    s.MemSendReq  = MemSendReq
  def setMemHasResp(s, MemHasResp):
    s.MemHasResp  = MemHasResp
  def setMemRecvResp(s, MemRecvResp):
    s.MemRecvResp = MemRecvResp

  # Interface
  def canReq(s):
    return s.MemCanReq(s.port_id)

  def sendReq(s, req):
    return s.MemSendReq(s.port_id, req)

  def hasResp(s):
    return s.MemHasResp(s.port_id)

  def recvResp(s):
    return s.MemRecvResp(s.port_id)

  # Everything must tick
  def tick(s):
    pass

  # Nothing happens
  def linetrace(s):
    return 7 * ' '
