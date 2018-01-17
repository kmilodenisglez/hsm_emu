BITCOIND=bitcoind
BITCOINGUI=bitcoin-qt
BITCOINCLI=bitcoin-cli
B1_FLAGS=
B2_FLAGS=
B1=-datadir=nodes/node_0 $(B1_FLAGS)
B2=-datadir=nodes/node_1 $(B2_FLAGS)
BLOCKS=1
GENBLOCKS=103 # para generar 150 BTC en la cuenta
ADDRESS=
AMOUNT=
ACCOUNT=

start:
	$(BITCOIND) $(B1) -daemon 
	$(BITCOIND) $(B2) -daemon

start-gui:
	$(BITCOINGUI) $(B1) &
	$(BITCOINGUI) $(B2) &

generate:
	$(BITCOINCLI) $(B1) generate $(BLOCKS)

generate-start:
	$(BITCOINCLI) $(B1) generate $(GENBLOCKS)

dumpwallet:
	$(BITCOINCLI) $(B1) dumpwallet node_0/wallet.txt

getinfo:
	$(BITCOINCLI) $(B1) getinfo
	$(BITCOINCLI) $(B2) getinfo

sendfrom1:
	$(BITCOINCLI) $(B1) sendtoaddress $(ADDRESS) $(AMOUNT)

sendfrom2:
	$(BITCOINCLI) $(B2) sendtoaddress $(ADDRESS) $(AMOUNT)

address1:
	$(BITCOINCLI) $(B1) getnewaddress $(ACCOUNT)

address2:
	$(BITCOINCLI) $(B2) getnewaddress $(ACCOUNT)

stop:
	$(BITCOINCLI) $(B1) stop
	$(BITCOINCLI) $(B2) stop

clean:
	find nodes/node_0/regtest/* -not -name 'server.*' -delete
	find nodes/node_1/regtest/* -not -name 'server.*' -delete
	find nodes/node_0/wallet.txt -delete	
