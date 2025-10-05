# Bitcoin Quantum Attack Simulator

## Overview

An educational Python simulation demonstrating how quantum computers could theoretically exploit Bitcoin's public key exposure during transactions. This project models the complete attack lifecycle—from mempool monitoring to Shor's algorithm execution to double-spend attacks via fee competition.

**⚠️ EDUCATIONAL PURPOSE ONLY**: This is a theoretical simulation. Current quantum computers cannot break Bitcoin's cryptography. Do not attempt real attacks.

## What It Does

The simulator creates a realistic Bitcoin network environment with:

- **Multiple quantum attackers** with varying capabilities (qubit counts, error rates, strategies)
- **Diverse wallet ecosystem** (P2PKH, P2WPKH, P2TR, multisig addresses)
- **Six attack scenarios** demonstrating different vulnerability patterns
- **Realistic timing mechanics** (10-minute block times, 2-3 minute quantum attacks)
- **Economic modeling** (fee competition, attack profitability analysis)
- **Probabilistic outcomes** (quantum decoherence, attack failures)

## Key Demonstrations

1. **Public Key Exposure**: Shows how ECDSA/Schnorr signatures necessarily reveal public keys
2. **Attack Window**: Proves ~10 minutes is sufficient for quantum key derivation
3. **Double-Spend Mechanism**: Demonstrates how attackers use higher fees to win miner selection
4. **Address Reuse Catastrophe**: Illustrates pre-computed attacks on reused addresses
5. **Address Type Vulnerability**: Confirms P2PKH, P2WPKH, and P2TR are equally vulnerable
6. **Economic Protection**: Shows small transactions may avoid attacks due to cost-benefit analysis

## Sample Output

```
⚡ QUANTUM ATTACK PHASE
🔬 ATTACKING: 1ce9f1ef731677648aa6...
├─ Target Value: 8.2000 BTC
├─ Attack time: 84.0s (block time remaining: 1184.9s)
✅ SUCCESS! Private keys derived
🏴‍☠️ COMPETING TRANSACTION CREATED:
└─ Fee: 1.0000 BTC (🔥 10.0x higher!)
```

## Installation

```bash
# Clone the repository
git clone https://github.com/DEEPML1818/Quantum-Computers-Attack-Bitcoin.git
cd Quantum-Computers-Attack-Bitcoin


# Run the simulation (Python 3.8+)
python3 bitcoin_quantum_simulator.py
```

No dependencies required—uses only Python standard library.

## How It Works

1. **Network Setup**: Creates Bitcoin network with realistic parameters
2. **Attacker Initialization**: Configures quantum computers (4000 qubits, 95% success rate)
3. **Wallet Creation**: Generates UTXOs across different address types
4. **Transaction Broadcast**: Exposes public keys in mempool
5. **Quantum Attack**: Simulates Shor's algorithm execution
6. **Double-Spend**: Creates competing transaction with higher fee
7. **Block Mining**: Miners select highest-fee transaction (attacker wins)

## Technical Details

- **Quantum Model**: 2000-4000 logical qubits required for secp256k1
- **Attack Time**: 120-180 seconds per key with parallel processing
- **Success Rate**: 85-95% (models decoherence and gate errors)
- **Fee Strategy**: Attackers pay 10x original fee or 50% of transaction value

## Educational Insights

This simulation teaches:

- Why Bitcoin is vulnerable to future quantum computers
- The critical role of public key exposure in transaction signing
- How economic incentives shape quantum attack strategies
- Why address reuse is catastrophic in a post-quantum world
- The importance of proactive migration to post-quantum cryptography

## Timeline

- **Current (2025)**: Quantum computers cannot break Bitcoin
- **Estimated Threat**: 10-30 years until cryptographically-relevant quantum computers
- **Required Action**: Begin planning post-quantum migration now

## Post-Quantum Solutions

The simulation demonstrates why Bitcoin needs:

- **SPHINCS+** (hash-based signatures)
- **Dilithium** (lattice-based signatures)
- **Falcon** (compact lattice signatures)

All are NIST-standardized and quantum-resistant.

## Limitations

This is a **simplified educational model**:

- Real Shor's algorithm implementation is far more complex
- Network propagation delays not fully modeled
- Mining pool behavior simplified
- Economic game theory abstracted

## Academic References

- Shor, P.W. (1997). "Polynomial-Time Algorithms for Prime Factorization and Discrete Logarithms"
- NIST Post-Quantum Cryptography Standardization (2024)
- Bitcoin Improvement Proposals (BIPs) on quantum resistance

## License

MIT License - Free for educational and research purposes

## Disclaimer

**This code is for educational purposes only.** It demonstrates theoretical attacks that are currently impossible. Do not use this knowledge for malicious purposes. The author assumes no liability for misuse.

---

**Contributing**: Issues and pull requests welcome for educational improvements

**Questions?**: See the accompanying technical documentation for detailed analysis
