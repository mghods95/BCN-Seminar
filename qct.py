"""
pqc_demo.py — Illustrative demo for "Post-Quantum Cryptography & Crypto risk"

What this demo shows (presentation-friendly):
1) Funds are locked to an "address" = hash(pubkey).
2) A spend transaction reveals the public key (as in many real-world designs at spend time).
3) An attacker with a Shor-like capability can recover the private key from the public key.
   - Here we SIMULATE that with brute force on a tiny toy curve.
4) The attacker forges a competing transaction and steals funds (mempool race analogy).

Notes:
- This is NOT Bitcoin/Ethereum cryptography. It is a pedagogical simulation.
- The "signature" scheme used here is toy Schnorr-like math to keep code short and verifiable:
    s = H(m) * d mod p
    verify: s*G == H(m)*Q
  It is not intended to be secure—only to demonstrate "forge after key recovery".

Run:
  python pqc_demo.py
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, Tuple, Dict
import hashlib


# -----------------------------
# Toy elliptic curve arithmetic
# -----------------------------

@dataclass(frozen=True)
class Curve:
    p: int
    a: int
    b: int


Point = Optional[Tuple[int, int]]  # None = point at infinity


def inv_mod(k: int, p: int) -> int:
    return pow(k, -1, p)


def is_on_curve(curve: Curve, P: Point) -> bool:
    if P is None:
        return True
    x, y = P
    return (y * y - (x * x * x + curve.a * x + curve.b)) % curve.p == 0


def add(curve: Curve, P: Point, Q: Point) -> Point:
    if P is None:
        return Q
    if Q is None:
        return P

    x1, y1 = P
    x2, y2 = Q
    p = curve.p

    # P + (-P) = O
    if x1 == x2 and (y1 + y2) % p == 0:
        return None

    if P != Q:
        m = ((y2 - y1) * inv_mod((x2 - x1) % p, p)) % p
    else:
        m = ((3 * x1 * x1 + curve.a) * inv_mod((2 * y1) % p, p)) % p

    x3 = (m * m - x1 - x2) % p
    y3 = (m * (x1 - x3) - y1) % p
    return (x3, y3)


def mul(curve: Curve, k: int, P: Point) -> Point:
    R = None
    N = P
    while k > 0:
        if k & 1:
            R = add(curve, R, N)
        N = add(curve, N, N)
        k >>= 1
    return R


def find_generator_point(curve: Curve, start_x: int = 0, max_tries: int = 10_000) -> Point:
    """
    Finds any point on the curve by scanning x and attempting to find y such that:
        y^2 ≡ x^3 + a x + b (mod p)
    For small p, brute scanning is fine. This avoids hardcoding a potentially invalid G.
    """
    p = curve.p
    for dx in range(max_tries):
        x = (start_x + dx) % p
        rhs = (x * x * x + curve.a * x + curve.b) % p
        # brute scan y
        for y in range(p):
            if (y * y) % p == rhs:
                P = (x, y)
                if is_on_curve(curve, P):
                    return P
    raise RuntimeError("Could not find a curve point; choose different parameters.")


# -----------------------------------------
# Toy "signature": Schnorr-like (toy only)
# -----------------------------------------

def H_to_int(msg: str, p: int) -> int:
    h = hashlib.sha256(msg.encode("utf-8")).digest()
    return int.from_bytes(h, "big") % p


def sign(curve: Curve, G: Point, d: int, msg: str) -> int:
    return (H_to_int(msg, curve.p) * d) % curve.p


def verify(curve: Curve, G: Point, Q: Point, msg: str, s: int) -> bool:
    left = mul(curve, s, G)
    right = mul(curve, H_to_int(msg, curve.p), Q)
    return left == right


# -----------------------------------------
# Address model + ledger model (toy)
# -----------------------------------------

def address_from_pubkey(Q: Point) -> str:
    # "address" is hash of pubkey (toy)
    assert Q is not None
    data = f"{Q[0]}:{Q[1]}".encode("utf-8")
    return hashlib.sha256(data).hexdigest()[:16]  # short for display


@dataclass
class Wallet:
    d: int
    Q: Point
    address: str


@dataclass
class Tx:
    frm_addr: str
    to_addr: str
    amount: int
    pubkey: Optional[Point]   # revealed on spend
    sig: Optional[int]        # signature
    note: str


class Ledger:
    def __init__(self):
        self.balances: Dict[str, int] = {}

    def mint(self, addr: str, amount: int):
        self.balances[addr] = self.balances.get(addr, 0) + amount

    def apply(self, tx: Tx, curve: Curve, G: Point) -> bool:
        if self.balances.get(tx.frm_addr, 0) < tx.amount:
            print("  [Ledger] Reject: insufficient funds.")
            return False

        # Spend requires pubkey + signature (reveals pubkey)
        if tx.pubkey is None or tx.sig is None:
            print("  [Ledger] Reject: missing pubkey/signature.")
            return False

        # Check that pubkey hashes to the from-address
        if address_from_pubkey(tx.pubkey) != tx.frm_addr:
            print("  [Ledger] Reject: pubkey does not match address.")
            return False

        # Verify signature authorizes spending to recipient for amount
        msg = f"pay {tx.amount} to {tx.to_addr}"
        print("  [Ledger] Verifying message:", repr(msg))

        if not verify(curve, G, tx.pubkey, msg, tx.sig):
            print("  [Ledger] Reject: invalid signature.")
            return False

        # Apply transfer
        self.balances[tx.frm_addr] -= tx.amount
        self.balances[tx.to_addr] = self.balances.get(tx.to_addr, 0) + tx.amount
        print("  [Ledger] Accepted.")
        return True


# -----------------------------------------
# "Quantum" attacker = solves discrete log
# -----------------------------------------

def recover_private_key_by_dlog(curve: Curve, G: Point, Q: Point, max_k: int = 50_000) -> Optional[int]:
    """
    This brute force stands in for Shor's algorithm in the real world.
    On real curves, classical brute force is infeasible; Shor makes it feasible.
    """
    R = None
    for k in range(1, max_k + 1):
        R = add(curve, R, G)  # incremental k*G
        if R == Q:
            return k
    return None


# -------------
# Demo runner
# -------------

def main():
    # Tiny curve for fast demo
    curve = Curve(p=233, a=1, b=1)

    # Auto-find a valid point so you never hit the "G not on curve" issue
    G = find_generator_point(curve, start_x=0)
    assert is_on_curve(curve, G)

    print("\n=== Curve Setup ===")
    print(f"Curve: y^2 = x^3 + {curve.a}x + {curve.b} (mod {curve.p})")
    print(f"Chosen generator point G: {G}")

    # Wallet owner (Alice)
    alice_d = 20  # small for quick demo
    alice_Q = mul(curve, alice_d, G)
    alice_addr = address_from_pubkey(alice_Q)
    alice = Wallet(d=alice_d, Q=alice_Q, address=alice_addr)

    # Attacker (Eve) doesn't need keys; just an address label
    eve_addr = "EVE000000000000"

    ledger = Ledger()
    ledger.mint(alice.address, 100)

    print("\n=== Initial State ===")
    print(f"Alice address (hash(pubkey)) : {alice.address}")
    print(f"Alice balance               : {ledger.balances[alice.address]}")
    print(f"Eve balance                 : {ledger.balances.get(eve_addr, 0)}")

    # Alice creates a legitimate payment to Bob (spend reveals pubkey)
    bob_addr = "BOB0000000000000"
    legit_msg = f"pay 10 to {bob_addr}"
    print("\n[Alice] Signing message:", repr(legit_msg))
    alice_sig = sign(curve, G, alice.d, legit_msg)

    tx_legit = Tx(
        frm_addr=alice.address,
        to_addr=bob_addr,
        amount=10,
        pubkey=alice.Q,     # revealed during spend
        sig=alice_sig,
        note="Alice pays Bob (pubkey revealed)"
    )

    print("\n=== Alice broadcasts a spend tx (pubkey revealed) ===")
    print(f"Tx note: {tx_legit.note}")
    print(f"Revealed pubkey Q: {tx_legit.pubkey}")

    # Attacker sees pubkey and "runs Shor" (simulated brute force)
    print("\n=== Eve runs 'quantum attack' to recover Alice private key from Q ===")
    recovered = recover_private_key_by_dlog(curve, G, tx_legit.pubkey, max_k=50_000)
    print(f"Recovered private key d: {recovered}")

    if recovered is None:
        print("Attack failed (increase max_k or choose different toy parameters).")
        return

    # Eve forges a competing spend from Alice to Eve
    forged_msg = f"pay 90 to {eve_addr}"
    print("\n[Eve] Forging message:", repr(forged_msg))
    forged_sig = sign(curve, G, recovered, forged_msg)

    tx_attack = Tx(
        frm_addr=alice.address,
        to_addr=eve_addr,
        amount=90,
        pubkey=tx_legit.pubkey,  # same revealed pubkey
        sig=forged_sig,
        note="Eve forges a spend using recovered private key"
    )

    print("\n=== Mempool race simulation ===")
    print("Eve uses Alice's revealed pubkey to create a competing spend.")
    print("Two spends from the same funds cannot both confirm; one wins (fee/race analogy).")

    print("\n=== Eve broadcasts forged tx ===")
    print(f"Tx note: {tx_attack.note}")
    print("Ledger verifies Eve's forged signature as valid...")
    ledger.apply(tx_attack, curve, G)

    print("\n=== Alice's legit tx attempts to confirm afterward ===")
    ledger.apply(tx_legit, curve, G)

    print("\n=== Final State ===")
    print(f"Alice balance : {ledger.balances.get(alice.address, 0)}")
    print(f"Bob balance   : {ledger.balances.get(bob_addr, 0)}")
    print(f"Eve balance   : {ledger.balances.get(eve_addr, 0)}")

    print("\nTakeaway:")
    print(" - On real curves, classical brute force is infeasible.")
    print(" - Shor makes 'recover d from Q' feasible => signatures become forgeable.")
    print(" - The exposure moment is when Q becomes visible on-chain / in the mempool.")


if __name__ == "__main__":
    main()