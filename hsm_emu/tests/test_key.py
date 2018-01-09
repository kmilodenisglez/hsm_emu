#!/usr/bin/env python3
import sys
if sys.version_info.major < 3:
	sys.stderr.write('Sorry, Python 3.x required by this example.\n')
	sys.exit(1)
	
from context import setup, ExtendedKey, PublicKey, PrivateKey

setup('regtest')
actived_mainnet = False

masterpriv_regtest  = 'tprv8ZgxMBicQKsPf4wpV8MBx9Ux4T7Cvnojkw6WMsKF6WQSTb76AinSxfjAC73f8GXZgfTczrE2U1sh2L8HJeyhbaBbjCmkdsTAAueN9HQsyvF'
masterpub_regtest   = 'tpubD6NzVbkrYhZ4XiSuFKUqSH6VDmBdB7BA2WhjSw9a2A8SkkcYrwxHNPq51rQywuWk3w1XchUC5ur6hsvtKhrMhSEva1ZBR39vvBvm4voFhoa'

priv = ExtendedKey.decode(masterpriv_regtest, check_network=actived_mainnet) #aqui no hace falta especificar mainnet, lo detecta x 1ro byte
masterpub = priv.pub()

derived = priv.derive("m/0'/0'/276'")

address_derived = derived.key.pub().to_address()
derived_wif = derived.key.to_wif()

derived_wif_base54 = derived.key.to_wif()
derived_hex = PrivateKey.from_wif(derived_wif_base54)
address_from_derived = PublicKey.from_priv(derived_hex).to_address()

derived_encode = derived.encode(mainnet=actived_mainnet)
derived_pub_encode = derived.pub().encode(mainnet=actived_mainnet)


print("|--------------------------------------------------|")
print("", priv.key.hexlify())
print("  masterpriv: ", masterpriv_regtest)
print("")
print("  masterpub: ", masterpub.encode(mainnet=actived_mainnet))
print("")
print("  masterpub (HEX): ", masterpub.key.hexlify())
print("")
print(" masterpriv (WIF):", priv.key.to_wif())
print("")
print("  derived of masterpriv: ",  derived_encode)
print("")
print("  derived privkey (HEX): ", derived.key.hexlify())
print("")
print(" derived privkey (WIF):", derived.key.to_wif())
print("")
print("  derived chaincode: ",derived.chaincode.hex())
print("")
print("  derived version: ", derived.get_version().hex())
print("")
print("  derived depth: ",derived.depth)
print("")
print("  derived fingerprint: ", derived.parent_fingerprint.hex())
print("")
print("  derived child index: ", derived.index)
print("")
print("")
print("  public derived of masterpriv", derived_pub_encode)
print("")
print("  private key derived (WIF): ",derived_wif)
print("")
print("  address derived: ", address_derived)
print("")
print("  publikey derived (HEX): ", derived.pub().key.hexlify())
print("")
assert address_derived == address_from_derived
assert ExtendedKey.decode(derived_pub_encode, check_network=actived_mainnet).key.to_address() == address_derived
print("  address from PublicKey: ", address_from_derived)
#print("  masterpriv decode: ", ExtendedKey.decode(masterpriv_regtest, check_network=True))
#print("  publikey decode: ", ExtendedKey.decode(priv.pub().encode(mainnet=False), check_network=True))
print("")
print("|--------------------------------------------------|")