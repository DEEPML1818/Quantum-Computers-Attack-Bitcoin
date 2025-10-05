#!/usr/bin/env python3
"""
Advanced Bitcoin Quantum Attack Simulator
Comprehensive simulation with multiple attack vectors, defense mechanisms, and scenarios.

⚠️  SIMULATION ONLY - Do not use on mainnet. For real experiments use regtest/testnet.
⚠️  Never reuse keys or attempt attacks on real wallets.
"""

import hashlib
import random
import time
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple
from enum import Enum
from collections import defaultdict

class AddressType(Enum):
    P2PKH = "P2PKH (Legacy)"
    P2WPKH = "P2WPKH (SegWit)"
    P2TR = "P2TR (Taproot)"
    P2SH_MULTISIG_2OF3 = "P2SH Multisig 2-of-3"
    P2WSH_MULTISIG_3OF5 = "P2WSH Multisig 3-of-5"

class TxStatus(Enum):
    CREATED = "Created"
    BROADCAST = "Broadcast to mempool"
    ATTACKED = "Under quantum attack"
    CONFIRMED = "Confirmed in block"
    STOLEN = "Stolen by quantum attacker"
    RBF_REPLACED = "Replaced by fee"

@dataclass
class QuantumComputer:
    """Represents a quantum computer with specific capabilities"""
    name: str
    qubits: int
    error_rate: float
    key_derivation_time: float  # seconds
    success_probability: float

    def can_break_secp256k1(self) -> bool:
        """Estimate if quantum computer is powerful enough"""
        # Shor's algorithm needs ~2000-4000 logical qubits for secp256k1
        return self.qubits >= 2000 and self.error_rate < 0.001

@dataclass
class Transaction:
    """Detailed transaction structure"""
    txid: str
    inputs: List['UTXO']
    outputs: List[Dict]
    fee: float
    pubkeys_exposed: List[str]
    signatures: List[str]
    status: TxStatus
    broadcast_time: float
    confirmation_time: Optional[float] = None
    rbf_enabled: bool = False
    locktime: int = 0
    witness_data: Optional[str] = None
    competing_txs: List[str] = field(default_factory=list)

@dataclass
class UTXO:
    """Unspent Transaction Output with full details"""
    txid: str
    vout: int
    address: str
    address_type: AddressType
    amount: float
    privkey: str
    pubkey: str
    pubkey_hash: str
    script_pubkey: str
    spent: bool = False
    pubkey_exposed: bool = False
    exposure_count: int = 0  # Track address reuse
    created_block: int = 0

@dataclass
class QuantumAttacker:
    """Sophisticated quantum attacker with strategy"""
    name: str
    quantum_computer: QuantumComputer
    btc_balance: float = 0.0
    successful_attacks: int = 0
    failed_attacks: int = 0
    total_stolen: float = 0.0
    attack_strategy: str = "AGGRESSIVE"  # AGGRESSIVE, SELECTIVE, OPPORTUNISTIC

    def should_attack(self, tx: Transaction) -> bool:
        """Decide if this transaction is worth attacking"""
        total_value = sum(inp.amount for inp in tx.inputs)

        if self.attack_strategy == "AGGRESSIVE":
            return total_value > 0.1  # Attack anything over 0.1 BTC
        elif self.attack_strategy == "SELECTIVE":
            return total_value > 5.0  # Only high-value targets
        else:  # OPPORTUNISTIC
            return total_value > 1.0 and random.random() > 0.5

    def estimate_attack_time(self, num_keys: int) -> float:
        """Calculate time needed to break N keys"""
        base_time = self.quantum_computer.key_derivation_time
        # Parallel processing efficiency
        return base_time * num_keys * 0.7

class BitcoinNetwork:
    """Simulates Bitcoin network with realistic mechanics"""

    def __init__(self):
        self.current_block = 850000
        self.current_time = time.time()
        self.block_time_avg = 600  # 10 minutes
        self.mempool: Dict[str, Transaction] = {}
        self.blockchain: List[Dict] = []
        self.utxo_set: List[UTXO] = []
        self.quantum_attackers: List[QuantumAttacker] = []
        self.network_hash_rate = 600_000_000  # TH/s
        self.difficulty_adjustment = 1.0

    def create_utxo(self, addr_type: AddressType, amount: float,
                    num_signers: int = 1) -> UTXO:
        """Create a UTXO with cryptographic details"""
        txid = hashlib.sha256(str(random.random()).encode()).hexdigest()

        # Generate keys
        privkey = hashlib.sha256(str(random.random()).encode()).hexdigest()
        pubkey = hashlib.sha256(privkey.encode()).hexdigest()
        pubkey_hash = hashlib.sha256(pubkey.encode()).hexdigest()[:40]

        # Create script based on address type
        if addr_type == AddressType.P2PKH:
            address = f"1{pubkey_hash[:33]}"
            script = f"OP_DUP OP_HASH160 {pubkey_hash[:40]} OP_EQUALVERIFY OP_CHECKSIG"
        elif addr_type == AddressType.P2WPKH:
            address = f"bc1q{pubkey_hash[:38]}"
            script = f"OP_0 {pubkey_hash[:40]}"
        elif addr_type == AddressType.P2TR:
            address = f"bc1p{pubkey_hash[:58]}"
            script = f"OP_1 {pubkey_hash[:64]}"
        elif "MULTISIG" in addr_type.value:
            address = f"3{pubkey_hash[:33]}"
            script = f"OP_{num_signers} ... OP_CHECKMULTISIG"
        else:
            address = f"1{pubkey_hash[:33]}"
            script = f"OP_DUP OP_HASH160 {pubkey_hash[:40]} OP_EQUALVERIFY OP_CHECKSIG"

        utxo = UTXO(
            txid=txid,
            vout=0,
            address=address,
            address_type=addr_type,
            amount=amount,
            privkey=privkey,
            pubkey=pubkey,
            pubkey_hash=pubkey_hash,
            script_pubkey=script,
            created_block=self.current_block
        )

        self.utxo_set.append(utxo)
        return utxo

    def create_transaction(self, inputs: List[UTXO], outputs: List[Dict],
                          fee: float, rbf: bool = False) -> Transaction:
        """Create a detailed Bitcoin transaction"""
        # Generate transaction ID
        tx_data = "".join([u.txid for u in inputs]) + str(random.random())
        txid = hashlib.sha256(tx_data.encode()).hexdigest()

        # Expose public keys (CRITICAL VULNERABILITY POINT)
        pubkeys_exposed = []
        signatures = []

        for utxo in inputs:
            if not utxo.pubkey_exposed:
                explain(f"   🔓 EXPOSING public key for {utxo.address[:20]}...")
                utxo.pubkey_exposed = True
                utxo.exposure_count += 1

            pubkeys_exposed.append(utxo.pubkey)
            # Create signature
            sig_data = txid + utxo.privkey
            signature = hashlib.sha256(sig_data.encode()).hexdigest()
            signatures.append(signature)

        tx = Transaction(
            txid=txid,
            inputs=inputs,
            outputs=outputs,
            fee=fee,
            pubkeys_exposed=pubkeys_exposed,
            signatures=signatures,
            status=TxStatus.CREATED,
            broadcast_time=self.current_time,
            rbf_enabled=rbf
        )

        return tx

    def broadcast_transaction(self, tx: Transaction):
        """Broadcast transaction to mempool"""
        print(f"\n   📡 Broadcasting transaction: {tx.txid[:32]}...")

        # Calculate transaction details
        total_input = sum(inp.amount for inp in tx.inputs)
        total_output = sum(out['amount'] for out in tx.outputs)

        print(f"   ├─ Inputs: {len(tx.inputs)} UTXOs = {total_input:.4f} BTC")
        print(f"   ├─ Outputs: {len(tx.outputs)} recipients = {total_output:.4f} BTC")
        print(f"   ├─ Fee: {tx.fee:.4f} BTC ({tx.fee/total_input*100:.2f}% of input)")
        print(f"   ├─ RBF Enabled: {'✓' if tx.rbf_enabled else '✗'}")
        print(f"   └─ Public Keys Exposed: {len(tx.pubkeys_exposed)}")

        for idx, pubkey in enumerate(tx.pubkeys_exposed):
            print(f"      • Input #{idx}: {pubkey[:40]}...")
            explain(f"        ⚠️  This public key can be used to derive the private key with Shor's algorithm!", 0.5)

        tx.status = TxStatus.BROADCAST
        self.mempool[tx.txid] = tx

        explain(f"Transaction is now in the mempool, visible to all nodes including quantum attackers!", 1.0)

    def quantum_attack_scan(self):
        """All quantum attackers scan mempool for targets"""
        print_section("⚡ QUANTUM ATTACK PHASE", "█")

        if not self.mempool:
            print("   ✓ Mempool is empty. No targets for quantum attackers.")
            return

        explain(f"There are {len(self.quantum_attackers)} quantum attackers monitoring the network...", 1.0)

        for attacker in self.quantum_attackers:
            print(f"\n🤖 {attacker.name} (Quantum Computer: {attacker.quantum_computer.qubits} qubits)")
            print(f"   Strategy: {attacker.attack_strategy}")
            print(f"   Success Rate: {attacker.quantum_computer.success_probability*100:.1f}%")
            print(f"   Key Derivation Time: {attacker.quantum_computer.key_derivation_time:.1f}s per key")

            targets_found = []

            for txid, tx in self.mempool.items():
                if tx.status == TxStatus.ATTACKED:
                    continue  # Already under attack

                if attacker.should_attack(tx):
                    targets_found.append(tx)

            if not targets_found:
                print(f"   ✓ No suitable targets found (strategy: {attacker.attack_strategy})")
                continue

            print(f"   🎯 Found {len(targets_found)} potential target(s)!")

            for tx in targets_found:
                self._execute_quantum_attack(attacker, tx)

    def _execute_quantum_attack(self, attacker: QuantumAttacker, tx: Transaction):
        """Execute a quantum attack on a specific transaction"""
        total_value = sum(inp.amount for inp in tx.inputs)

        print(f"\n   🔬 ATTACKING: {tx.txid[:32]}...")
        print(f"   ├─ Target Value: {total_value:.4f} BTC")
        print(f"   ├─ Public Keys to Break: {len(tx.pubkeys_exposed)}")
        print(f"   └─ Original Fee: {tx.fee:.4f} BTC")

        # Estimate attack time
        attack_time = attacker.estimate_attack_time(len(tx.pubkeys_exposed))
        block_time_remaining = self.block_time_avg - (time.time() - tx.broadcast_time)

        explain(f"Estimated attack time: {attack_time:.1f}s", 0.5)
        explain(f"Time until next block: ~{block_time_remaining:.1f}s", 0.5)

        if attack_time > block_time_remaining:
            print(f"   ⚠️  ATTACK TOO SLOW: Block will be mined before attack completes!")
            attacker.failed_attacks += 1
            return

        # Simulate Shor's algorithm
        print(f"\n   ⚙️  Running Shor's Algorithm on quantum computer...")
        print(f"   ├─ Initializing {attacker.quantum_computer.qubits} qubits")
        print(f"   ├─ Creating superposition states")
        print(f"   ├─ Applying quantum Fourier transform")
        print(f"   └─ Measuring and calculating discrete logarithm")

        for i in range(4):
            progress = (i + 1) * 25
            bar = '█' * (i + 1) + '░' * (3 - i)
            print(f"   {bar} {progress}% - Processing qubit entanglements...")
            time.sleep(0.4)

        # Check success based on quantum computer capabilities
        if random.random() > attacker.quantum_computer.success_probability:
            print(f"   ❌ ATTACK FAILED: Quantum decoherence error!")
            attacker.failed_attacks += 1
            return

        print(f"   ✅ SUCCESS! Private keys derived:")
        for idx, inp in enumerate(tx.inputs):
            print(f"      • Input #{idx}: privkey = {inp.privkey[:40]}...")

        # Create competing transaction
        explain("Creating competing transaction with MAXIMUM FEE...", 1.0)

        attacker_address = f"bc1q_quantum_attacker_{attacker.name}_{random.randint(1000,9999)}"

        # Calculate attack transaction fee (much higher)
        attack_fee = min(tx.fee * 10, total_value * 0.5)  # 10x or 50% of value
        attack_output_value = total_value - attack_fee

        competing_txid = hashlib.sha256(f"attack{tx.txid}{attacker.name}".encode()).hexdigest()

        print(f"\n   🏴‍☠️ COMPETING TRANSACTION CREATED:")
        print(f"   ├─ TxID: {competing_txid[:32]}...")
        print(f"   ├─ Inputs: Same as victim (double-spend)")
        print(f"   ├─ Output: {attacker_address}")
        print(f"   ├─ Amount: {attack_output_value:.4f} BTC")
        print(f"   └─ Fee: {attack_fee:.4f} BTC (🔥 {attack_fee/tx.fee:.1f}x higher!)")

        explain("Broadcasting competing transaction to network...", 1.0)

        tx.status = TxStatus.ATTACKED
        tx.competing_txs.append(competing_txid)

        # Store attack details
        if not hasattr(tx, 'attack_details'):
            tx.attack_details = []

        tx.attack_details.append({
            'attacker': attacker.name,
            'competing_txid': competing_txid,
            'attack_fee': attack_fee,
            'destination': attacker_address,
            'value': attack_output_value
        })

        explain(f"⚠️  CRITICAL: Two transactions now spending the same inputs!", 1.0)
        explain(f"Miners will choose the one with HIGHER FEE = the quantum attack!", 1.5)

    def mine_block(self):
        """Simulate block mining and transaction selection"""
        print_section(f"⛏️  MINING BLOCK {self.current_block}", "═")

        if not self.mempool:
            print("   ✓ Mempool empty, mining empty block")
            self.current_block += 1
            return

        explain("Miners are selecting transactions based on fee priority...", 1.0)

        # Sort transactions by fee rate
        tx_list = list(self.mempool.values())
        tx_list.sort(key=lambda t: t.fee / sum(i.amount for i in t.inputs), reverse=True)

        print(f"\n   📋 Transaction Priority Queue (by fee rate):")
        for idx, tx in enumerate(tx_list[:5]):
            fee_rate = tx.fee / sum(i.amount for i in tx.inputs) * 100
            status_icon = "⚡" if tx.status == TxStatus.ATTACKED else "✓"
            print(f"   {idx+1}. {status_icon} {tx.txid[:24]}... | Fee: {tx.fee:.4f} BTC ({fee_rate:.2f}%)")

        # Process transactions
        confirmed_txs = []
        double_spend_groups = defaultdict(list)

        # Group conflicting transactions (double-spends)
        for tx in tx_list:
            input_key = tuple(sorted([f"{inp.txid}:{inp.vout}" for inp in tx.inputs]))
            double_spend_groups[input_key].append(tx)

        explain("\n   🔍 Detecting double-spend attempts...", 1.0)

        for input_key, conflicting_txs in double_spend_groups.items():
            if len(conflicting_txs) > 1:
                print(f"\n   ⚠️  DOUBLE-SPEND DETECTED: {len(conflicting_txs)} transactions spending same inputs!")

                # Sort by fee
                conflicting_txs.sort(key=lambda t: t.fee, reverse=True)

                winner = conflicting_txs[0]
                losers = conflicting_txs[1:]

                print(f"   ├─ Winner (highest fee): {winner.txid[:24]}... | Fee: {winner.fee:.4f} BTC")

                if winner.status == TxStatus.ATTACKED:
                    print(f"   └─ 💀 QUANTUM ATTACK SUCCESSFUL!")

                    for detail in winner.attack_details:
                        print(f"       • Attacker: {detail['attacker']}")
                        print(f"       • Stolen: {detail['value']:.4f} BTC")
                        print(f"       • Destination: {detail['destination']}")

                        # Update attacker stats
                        for attacker in self.quantum_attackers:
                            if attacker.name == detail['attacker']:
                                attacker.successful_attacks += 1
                                attacker.total_stolen += detail['value']
                                attacker.btc_balance += detail['value']

                    winner.status = TxStatus.STOLEN
                else:
                    print(f"   └─ ✓ Legitimate transaction confirmed")
                    winner.status = TxStatus.CONFIRMED

                for loser in losers:
                    print(f"   └─ Rejected: {loser.txid[:24]}... (lower fee)")

                confirmed_txs.append(winner)
            else:
                tx = conflicting_txs[0]
                tx.status = TxStatus.CONFIRMED
                confirmed_txs.append(tx)

        print(f"\n   ✓ Block {self.current_block} mined with {len(confirmed_txs)} transaction(s)")

        # Clear mempool
        self.mempool.clear()
        self.current_block += 1
        self.current_time += self.block_time_avg

def print_section(title: str, symbol: str = "="):
    """Print formatted section header"""
    print(f"\n{symbol * 75}")
    print(f"{title.center(75)}")
    print(f"{symbol * 75}\n")

def explain(text: str, pause: float = 0.8):
    """Print explanation with pause"""
    print(f"💡 {text}")
    time.sleep(pause)

def step(number: int, title: str, description: str = ""):
    """Print numbered step"""
    print(f"\n{'═' * 75}")
    print(f"STEP {number}: {title}")
    if description:
        print(f"{'─' * 75}")
        print(f"{description}")
    print(f"{'═' * 75}")

def run_advanced_simulation():
    """Run comprehensive quantum attack demonstration"""
    print_section("🚀 ADVANCED BITCOIN QUANTUM ATTACK SIMULATOR", "█")
    print("Comprehensive Educational Demonstration with Multiple Attack Scenarios")
    print("⚠️  SIMULATION ONLY - NOT FOR REAL ATTACKS")
    print("─" * 75)

    # Initialize network
    network = BitcoinNetwork()

    # Create quantum attackers with different capabilities
    step(1, "INITIALIZING QUANTUM ATTACKERS",
         "Creating quantum computers with varying capabilities")

    qc1 = QuantumComputer(
        name="IBM Quantum-X",
        qubits=4000,
        error_rate=0.0005,
        key_derivation_time=120,  # 2 minutes
        success_probability=0.95
    )

    qc2 = QuantumComputer(
        name="Google Sycamore-II",
        qubits=3000,
        error_rate=0.001,
        key_derivation_time=180,  # 3 minutes
        success_probability=0.85
    )

    attacker1 = QuantumAttacker("QuantumPirate", qc1, attack_strategy="AGGRESSIVE")
    attacker2 = QuantumAttacker("CryptoThief", qc2, attack_strategy="SELECTIVE")

    network.quantum_attackers.extend([attacker1, attacker2])

    print(f"\n   🤖 Attacker #1: {attacker1.name}")
    print(f"   ├─ Quantum Computer: {qc1.name}")
    print(f"   ├─ Qubits: {qc1.qubits}")
    print(f"   ├─ Can break secp256k1: {'✓ YES' if qc1.can_break_secp256k1() else '✗ NO'}")
    print(f"   └─ Strategy: {attacker1.attack_strategy}")

    print(f"\n   🤖 Attacker #2: {attacker2.name}")
    print(f"   ├─ Quantum Computer: {qc2.name}")
    print(f"   ├─ Qubits: {qc2.qubits}")
    print(f"   ├─ Can break secp256k1: {'✓ YES' if qc2.can_break_secp256k1() else '✗ NO'}")
    print(f"   └─ Strategy: {attacker2.attack_strategy}")

    time.sleep(2)

    # Create diverse wallet ecosystem
    step(2, "CREATING BITCOIN WALLET ECOSYSTEM",
         "Various users with different address types and spending patterns")

    print("\n   👤 Creating wallets:")

    alice_legacy = network.create_utxo(AddressType.P2PKH, 15.5)
    print(f"   ✓ Alice (Legacy P2PKH): {alice_legacy.amount} BTC - {alice_legacy.address[:30]}...")

    bob_segwit = network.create_utxo(AddressType.P2WPKH, 8.2)
    print(f"   ✓ Bob (SegWit): {bob_segwit.amount} BTC - {bob_segwit.address[:30]}...")

    carol_taproot = network.create_utxo(AddressType.P2TR, 22.0)
    print(f"   ✓ Carol (Taproot): {carol_taproot.amount} BTC - {carol_taproot.address[:30]}...")

    dave_multisig = network.create_utxo(AddressType.P2SH_MULTISIG_2OF3, 50.0, num_signers=2)
    print(f"   ✓ Dave (2-of-3 Multisig): {dave_multisig.amount} BTC - {dave_multisig.address[:30]}...")

    eve_whale = network.create_utxo(AddressType.P2WPKH, 100.0)
    print(f"   ✓ Eve (Whale): {eve_whale.amount} BTC - {eve_whale.address[:30]}...")

    frank_small = network.create_utxo(AddressType.P2PKH, 0.05)
    print(f"   ✓ Frank (Small holder): {frank_small.amount} BTC - {frank_small.address[:30]}...")

    explain(f"\n✓ Total ecosystem: {sum(u.amount for u in network.utxo_set):.2f} BTC across {len(network.utxo_set)} UTXOs", 2.0)

    # Scenario 1: Small transaction (ignored by attackers)
    step(3, "SCENARIO 1: Small Transaction",
         "Frank sends a small amount - will attackers bother?")

    tx1 = network.create_transaction(
        inputs=[frank_small],
        outputs=[{"address": "bc1q_merchant_small", "amount": 0.045}],
        fee=0.005,
        rbf=False
    )

    network.broadcast_transaction(tx1)
    network.quantum_attack_scan()
    network.mine_block()

    # Scenario 2: Medium transaction with RBF
    step(4, "SCENARIO 2: Medium Transaction with Replace-by-Fee",
         "Bob attempts a transaction with RBF enabled")

    tx2 = network.create_transaction(
        inputs=[bob_segwit],
        outputs=[{"address": "bc1q_bobs_recipient", "amount": 8.1}],
        fee=0.1,
        rbf=True
    )

    network.broadcast_transaction(tx2)
    explain("RBF allows replacing this transaction with a higher fee version", 1.0)
    explain("But quantum attackers can also use this mechanism!", 1.5)

    network.quantum_attack_scan()
    network.mine_block()

    # Scenario 3: High-value transaction (attractive target)
    step(5, "SCENARIO 3: High-Value Taproot Transaction",
         "Carol sends 22 BTC - prime target for quantum attack")

    tx3 = network.create_transaction(
        inputs=[carol_taproot],
        outputs=[{"address": "bc1p_carol_recipient_taproot", "amount": 21.8}],
        fee=0.2,
        rbf=False
    )

    network.broadcast_transaction(tx3)
    network.quantum_attack_scan()
    network.mine_block()

    # Scenario 4: Multisig (more complex)
    step(6, "SCENARIO 4: Multisig Transaction",
         "Dave's 2-of-3 multisig - multiple public keys exposed")

    explain("Multisig transactions expose MULTIPLE public keys!", 1.0)
    explain("Attackers must break multiple keys, increasing attack time", 1.0)

    tx4 = network.create_transaction(
        inputs=[dave_multisig],
        outputs=[{"address": "3_business_payment", "amount": 49.5}],
        fee=0.5,
        rbf=False
    )

    network.broadcast_transaction(tx4)
    network.quantum_attack_scan()
    network.mine_block()

    # Scenario 5: Whale transaction (everyone wants it)
    step(7, "SCENARIO 5: Whale Transaction - Multiple Attackers Compete",
         "Eve sends 100 BTC - all quantum attackers target this!")

    tx5 = network.create_transaction(
        inputs=[eve_whale],
        outputs=[{"address": "bc1q_exchange_deposit", "amount": 99.5}],
        fee=0.5,
        rbf=False
    )

    network.broadcast_transaction(tx5)
    explain("⚠️  HIGH-VALUE TARGET: All quantum attackers will attempt this!", 1.5)
    network.quantum_attack_scan()
    network.mine_block()

    # Scenario 6: Address reuse (already exposed)
    step(8, "SCENARIO 6: Address Reuse Attack",
         "Alice reuses her P2PKH address - public key already known!")

    alice_reused = network.create_utxo(AddressType.P2PKH, 10.0)
    alice_reused.pubkey = alice_legacy.pubkey  # Same address, pubkey already exposed
    alice_reused.pubkey_exposed = True
    alice_reused.exposure_count = 2

    explain("⚠️  CRITICAL VULNERABILITY: This address was already used!", 1.0)
    explain("The public key is already known from the previous transaction!", 1.0)
    explain("Attackers don't need to wait for mempool - they can prepare in advance!", 1.5)

    tx6 = network.create_transaction(
        inputs=[alice_reused],
        outputs=[{"address": "1_alice_new_recipient", "amount": 9.9}],
        fee=0.1,
        rbf=False
    )

    network.broadcast_transaction(tx6)
    explain("Quantum attackers had a HEAD START on this one!", 1.0)
    network.quantum_attack_scan()
    network.mine_block()

    # Final comprehensive report
    print_section("📊 COMPREHENSIVE SIMULATION REPORT", "█")

    total_btc = sum(u.amount for u in network.utxo_set)
    spent_btc = sum(u.amount for u in network.utxo_set if u.spent)

    print(f"Network Statistics:")
    print(f"├─ Current Block: {network.current_block}")
    print(f"├─ Total Value: {total_btc:.2f} BTC")
    print(f"├─ Spent Value: {spent_btc:.2f} BTC")
    print(f"└─ Remaining: {total_btc - spent_btc:.2f} BTC")

    print(f"\n{'─' * 75}")
    print("Quantum Attacker Results:")
    print(f"{'─' * 75}")

    for attacker in network.quantum_attackers:
        print(f"\n🤖 {attacker.name}")
        print(f"├─ Strategy: {attacker.attack_strategy}")
        print(f"├─ Successful Attacks: {attacker.successful_attacks}")
        print(f"├─ Failed Attacks: {attacker.failed_attacks}")
        print(f"├─ Success Rate: {attacker.successful_attacks/(attacker.successful_attacks + attacker.failed_attacks)*100:.1f}%"
              if (attacker.successful_attacks + attacker.failed_attacks) > 0 else "├─ Success Rate: N/A")
        print(f"├─ Total Stolen: {attacker.total_stolen:.4f} BTC")
        print(f"└─ Current Balance: {attacker.btc_balance:.4f} BTC")

    # Educational summary
    print(f"\n{'═' * 75}")
    print("📚 KEY INSIGHTS FOR YOUR ARTICLE:")
    print(f"{'═' * 75}\n")

    insights = [
        ("PUBLIC KEY EXPOSURE IS EVERYTHING",
         "• Addresses only show the hash until you spend\n" +
         "• The moment you broadcast a transaction, the full public key is visible\n" +
         "• This is unavoidable - ECDSA signatures require it"),

        ("THE ATTACK WINDOW",
         "• Average block time: 10 minutes\n" +
         "• Quantum key derivation: 2-3 minutes (with future hardware)\n" +
         "• Attackers have plenty of time to create competing transactions"),

        ("FEE COMPETITION IS THE WEAPON",
         "• Quantum attackers will pay MUCH higher fees\n" +
         "• Miners prioritize transactions by fee\n" +
         "• Legitimate users lose even with RBF enabled"),

        ("ADDRESS REUSE IS CATASTROPHIC",
         "• Reused addresses = public key already known\n" +
         "• Attackers can prepare the attack BEFORE you broadcast\n" +
         "• Zero-confirmation attacks become trivial"),

        ("VALUE MATTERS",
         "• High-value transactions are priority targets\n" +
         "• Small transactions may not be worth the quantum computation cost\n" +
         "• Strategic attackers will be selective"),

        ("MULTISIG PROVIDES MINIMAL PROTECTION",
         "• Requires breaking multiple keys\n" +
         "• Increases attack time but not by much (parallel processing)\n" +
         "• Still vulnerable within the 10-minute window"),

        ("ALL ADDRESS TYPES ARE VULNERABLE",
         "• P2PKH, P2WPKH, P2TR - all expose pubkeys when spending\n" +
         "• Taproot doesn't provide quantum resistance\n" +
         "• The address format is irrelevant to the quantum threat"),

        ("MITIGATION STRATEGIES",
         "• Never reuse addresses (spend entire UTXO)\n" +
         "• Use maximum fees for critical transactions\n" +
         "• Time-locked transactions provide limited protection\n" +
         "• Long-term: Need post-quantum signature schemes (SPHINCS+, Dilithium)")
    ]

    for idx, (title, content) in enumerate(insights, 1):
        print(f"{idx}. {title}")
        print(f"   {content}\n")

    print(f"{'═' * 75}")
    print("⚠️  This simulation demonstrates THEORETICAL attacks only")
    print("Current quantum computers cannot yet break Bitcoin's cryptography")
    print("This represents a future threat requiring proactive mitigation")
    print(f"{'═' * 75}\n")

if __name__ == "__main__":
    run_advanced_simulation()
