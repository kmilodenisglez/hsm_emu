#!/usr/bin/env python3
import sys
if sys.version_info.major < 3:
	sys.stderr.write('Sorry, Python 3.x required by this example.\n')
	sys.exit(1)

import os
from libraries import web
import json
from libraries.utils_wallets import setup, customPathDerivation, getXPubKey, signMessage, verifyMessage, bip32KeyInfoFromKey

# to avoid any path issues, "cd" to the web root.
web_root = os.path.abspath(os.path.dirname(__file__))
os.chdir(web_root)

#setup('regtest')
masterkey = 'tprv8ZgxMBicQKsPf4wpV8MBx9Ux4T7Cvnojkw6WMsKF6WQSTb76AinSxfjAC73f8GXZgfTczrE2U1sh2L8HJeyhbaBbjCmkdsTAAueN9HQsyvF'

def make_text(string):
	return string

urls = (
	#'/(.*)/', 'redirect', 
	"/", "index",
	"/login", "login",
	"/getxpub", "getxpub",
	"/signmessage", "signmessage",
	"/verifymessage", "verifymessage",
	"/bip32", "bip32", 
	"/derivation", "derivation", 
	)

render = web.template.render('templates', base='base')

app = web.application(urls, globals())

class redirect:
	def GET(self, path):
		web.seeother('/' + path)

class index:        
	def GET(self):
		return render.index("")

class login:        
	def GET(self):
		return render.login("View not implement yet")        

class getxpub:
	def GET(self):
		return render.xpubkey("Your pubkey goes here.")
		
	def POST(self):
		form = web.input(path={})
		#form.validates()
		print(form)
		path = form['path']
		pubkey = ['','','']
		if(len(path) > 4): #validar con re (Regular expression)
			pubkey = getXPubKey(path, masterkey)
		
		return make_text("<b>HD pubkey:</b> "+pubkey[0]+"</br></br> <b>HEX pubkey:</b> "+str(pubkey[1])
			+"</br></br> <b>Address:</b> "+str(pubkey[2]))

class signmessage:
	def GET(self):        
		return render.signmsg()
		
	def POST(self):
		values = web.input(path={},message={})
		res = signMessage(values['path'], values['message'], masterkey)        
		print(res[0], res[1])        
		#return make_text(res[0])
		return json.dumps({'address':str(res[0]), 'signature':res[1].decode()})

class verifymessage:
	def GET(self):        
		return render.signmsg()

	def POST(self):
		try:
			values = web.input(address={},signature={},message={})        
			print(values['address'], values['signature'], values['message'])        
			verified = verifyMessage(values['address'], values['signature'], values['message'])

			return json.dumps({'verified':verified})
		except Exception:
			print("Exception!!!")

class bip32:
	def GET(self):
		return render.bip32("")
		
	def POST(self):
		values = web.input(bip32Key={})
		title = 'Master Key'
		try:
			keyInfo = bip32KeyInfoFromKey(values['bip32Key'])
			if not keyInfo.is_master():
				title = 'Derived Key'
		except Exception as e:
			return json.dumps(
				{
					'error': True,
					'message': str(e),
				})            
		return json.dumps(
			{
				'error': False,
				'message': '', 
				'title': title,           
				'version':keyInfo.get_version().hex(), 
				'depth':keyInfo.depth,
				'parentFingerprint':keyInfo.parent_fingerprint.hex(),
				'childIndex':keyInfo.index,
				'chainCode':keyInfo.chaincode.hex(),
				'key':keyInfo.key.to_wif(),
			})

class derivation:        
	def POST(self):
		values = web.input(bip32Key={}, b32Path={})
		try:
			res = customPathDerivation(values['bip32Key'], values['b32Path'])
		except Exception as e:
			print(e)
			return json.dumps(
				{
					'error': True,
					'message': str(e),
				})
		res.update({'error': False, 'message': '',})
		return json.dumps(res)

if __name__ == '__main__':
	app.run()

