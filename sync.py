from blockchain import BlockChain
from typing import List, Optional, Tuple

import random
import socket
import struct
import time

SockAddr = Tuple[str, int]

class Sync:
    kBufLen : int = 65536
    kNBlock : int = 12
    kZBlock : int = 120

    kRvPll : bytes = b'\x98\x85\xce\x94'
    # [header, 4B] [seqnum, 4B] [beg height, 2B] [end height, 2B]
    kRvPsh : bytes = b'\x98\x85\xce\xc1'
    # [header, 4B] [seqnum, 4B] [max height, 2B] [blocks, 120B each]
    kNmPsh : bytes = b'\x98\x85\xce\xf8'
    # [header, 4B] [seqnum, 4B] [max height, 2B] [blocks, 120B each]

    def __init__(self, bc: BlockChain, localAddr : SockAddr, peersAddr : List[SockAddr], rto : float) -> None:
        self._bc = bc
        self._peers = peersAddr
        self._peers.remove(localAddr)
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._sock.setblocking(False)
        self._sock.bind(localAddr)
        self._buf = bytes(kBufLen)
        self._rto = rto
        self._seq = 0

    def DoSync() -> None:
        while True:
            res = _RecvPending()
            if res is None:
                break
            _Recover(res)
        _RandomPush()

    def _RecvPending() -> Optional[bool]:
        while True:
            (peer, pkt) = _RecvPkt(False)
            if peer is None:
                break
            if pkt[0] == kNmPsh:
                res = _OnNmPsh(peer, pkt[1], pkt[2], pkt[3])
                if res is not None:
                    return res
            elif pkt[0] == kRvPll:
                _OnRvPll(peer, pkt[1], pkt[2], pkt[3])
        return None
    
    def _RandomPush() -> None:
        for peer in random.sample(self._peers, 2):
            _DoNmPsh(peer)

    def _Recover(shrink: bool) -> None:
        if shrink:
            _Shrink()
        while True:
            hbeg = self._bc.GetHeight()
            hend = hbeg + kNBlock
            pshs: List[Tuple[int, bytes]] = None
            while not pshs:
                pshs = _PullRound(hbeg, hend)
                pshs = [psh for psh in pshs if psh[0] >= self._bc.GetHeight()]
            hmax = 0
            for psh in pshs:
                hmax = max(hmax, psh[0])
            res = 1
            if len[pshs] == 1:
                res = self._bc.Update(pshs[0][1], False)
            elif pshs[0][0] > pshs[1][0]:
                res = self._bc.Update(pshs[0][1], False)
            elif pshs[1][0] > pshs[0][0]:
                res = self._bc.Update(pshs[1][1], False)
            else:
                res = self._bc.Update(pshs[0][1], False)
                if res == 1:
                    res = self._bc.Update(pshs[1][1], False)
                else:
                    self._bc.Update(pshs[1][1], False)
            if res == 1:
                _Shrink()
            if hmax < self._bc.GetHeight() + 6:
                break

    def _Shrink() -> None:
        hmax = self._bc.GetHeight()
        res = 1
        while res == 1:
            hbeg = max(0, hmax - kNBlock)
            pshs: List[Tuple[int, bytes]] = None
            while not pshs:
                pshs = _PullRound(hbeg, hmax)
                pshs = [psh for psh in pshs if psh[0] >= self._bc.GetHeight()]
            if len[pshs] == 1:
                res = self._bc.Update(pshs[0][1], True)
            elif pshs[0][0] > pshs[1][0]:
                res = self._bc.Update(pshs[0][1], True)
            elif pshs[1][0] > pshs[0][0]:
                res = self._bc.Update(pshs[1][1], True)
            else:
                res = self._bc.Update(pshs[0][1], True)
                if res == 1:
                    res = self._bc.Update(pshs[1][1], True)
                else:
                    self._bc.Update(pshs[1][1], False)
    
    def _PullRound(hbeg: int, hend: int) -> List[Tuple[int, bytes]]:
        seqs = [_DoRvPll(peer, hbeg, hend) for peer in random.sample(self._peers, 2)]
        pshs: List[Tuple[int, bytes]] = list()
        due = time.time() + self._rto
        while True:
            while True:
                (peer, pkt) = _RecvPkt()
                if peer is None:
                    break
                if pkt[0] != kRvPsh:
                    continue
                if pkt[1] not in seqs:
                    continue
                pshs += (pkt[2], pkt[3])
                if len(pkts) == 2:
                    return pshs
            time.sleep(0.020)
            if time.time() > due:
                break
        return pshs

    def _OnNmPsh(peer: SockAddr, seqnum: int, hmax: int, blocks: bytes) -> Optional[bool]:
        if seqnum != 0:
            return None
        if hmax < self._bc.GetHeight():
            _DoNmPsh(peer)
            return None
        res = self._bc.Update(blocks, False)
        if res == 0:
            return False
        elif res == 1:
            return True
        elif res == 2:
            _DoNmPsh(peer)
        return None

    def _OnRvPll(peer: SockAddr, seqnum: int, hbeg: int, hend: int) -> None:
        hmax = self._bc.GetHeight()
        blocks = self._bc.GetRangeRaw(hbeg, hend)
        self._sock.sendto(struct.pack('<sLHs', kRvPsh, seqnum, hmax, blocks))

    def _DoRvPll(peer: SockAddr, hbeg: int, hend: int) -> int:
        seqnum = self._seq
        self._seq += 1
        self._sock.sendto(struct.pack('<sLHH', kRvPll, seqnum, hbeg, hend))
        return seqnum

    def _DoNmPsh(peer: SockAddr) -> None:
        hmax = self._bc.GetHeight()
        hbeg = max(0, hmax - kNBlock)
        blocks = self._bc.GetRangeRaw(hbeg, hmax)
        self._sock.sendto(struct.pack('<sLHs', kNmPsh, 0, hmax, blocks))
    
    def _RecvPkt() -> Tuple[Optional[SockAddr], Optional[tuple]]:
        while True:
            (res, peer) = self._sock.recvfrom_into(self._buf, len(self._buf))
            if res == -1:
                break
            if res < 8:
                continue
            header = self._buf[:4]
            if header == kNmPsh or header == kRvPsh:
                if res < 10 or (res - 10) % kZBlock != 0:
                    continue
                (seqnum, hmax) = struct.unpack('<LH', self._buf[4:])
                blocks = self._buf[10:res]
                return (peer, (header, seqnum, hmax, blocks))
            elif header == kRvPll:
                if res != 12:
                    continue
                (seqnum, hbeg, hend) = struct.unpack('<LHH', self._buf[4:])
                return (peer, (header, seqnum, hbeg, hend))
        return (None, None)
