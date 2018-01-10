#!/usr/bin/env python3
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
if sys.version_info.major < 3:
	sys.stderr.write('Sorry, Python 3.x required by this example.\n')
	sys.exit(1)

import json
from urllib.parse import urlparse
from libraries import web
from libraries.authentication import (getChallengeHidden, getChallengeVisual, 
	checkPath, signAuth, verifyAuth)
from libraries.utils_wallets import (setup, customPathDerivation,  
	getXPubKey, signMessage, verifyMessage, bip32KeyInfoFromKey, 
	cipherKeyValue, decipherKeyValue)

# to avoid any path issues, "cd" to the web root.
web_root = os.path.abspath(os.path.dirname(__file__))
os.chdir(web_root)

#setup('regtest')
masterkey = 'tprv8ZgxMBicQKsPf4wpV8MBx9Ux4T7Cvnojkw6WMsKF6WQSTb76AinSxfjAC73f8GXZgfTczrE2U1sh2L8HJeyhbaBbjCmkdsTAAueN9HQsyvF'


def make_text(string):
	return string


urls = (
	#'/(.*)/', 'redirect', 
	"/", "indexView",
	"/login", "loginView",
	"/verifyAuth", "verifySignAuthView",
	"/getxpub", "getxpubView",
	"/signmessage", "signMessageView",
	"/verifymessage", "verifyMessageView",
	"/cipherKeyValue", "symmetricEncryptView",
	"/decipherKeyValue", "symmetricDecryptView",
	"/bip32", "bip32View", 
	"/derivation", "derivationView", 
	)


render = web.template.render('templates', base='base')
app = web.application(urls, globals())


class redirect:
	def GET(self, path):
		web.seeother('/' + path)


class indexView:        
	def GET(self):
		return render.index("")


class loginView:        
	def GET(self):		
		challengeVisual = getChallengeVisual()
		challengeHiden = getChallengeHidden()
		
		return render.login(challengeVisual, challengeHiden)

	def POST(self):
		form = web.input(challengeHidden={}, challengeVisual={})		
		url = urlparse('http://satoshi@'+web.ctx.host+'/login?1')#http://satoshi@ip:port/login?1
		hdkeypath = checkPath(url)		
		res = signAuth(form['challengeHidden'], form['challengeVisual'], hdkeypath)

		return json.dumps(
			{
				'address':str(res[0]), 
				'signature':res[1].decode(), 
				'publicKey':res[2],
			})


class verifySignAuthView:
	def GET(self):
		return render.verifyAuth("Test implementation of the server-side signature verification")

	def POST(self):
		form = web.input(address={}, challengeHidden={}, challengeVisual={}, signature={})
		try:
			verified = verifyAuth(form['challengeHidden'], form['challengeVisual'], form['address'], form['signature'].encode())			
		except Exception as e:			
			return json.dumps(
				{
					'error': True,
					'message': str(e),
					'verified': False,
				})
		return json.dumps(
			{
				'error': False,
				'message': '', 
				'verified':verified,          
			})


class getxpubView:
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


class signMessageView:
	def GET(self):        
		return render.signmsg()
		
	def POST(self):
		try:		
			values = web.input(path={},message={})
			res = signMessage(values['path'], values['message'], masterkey)
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
				'address':str(res[0]),
				'signature':res[1].decode(),
			})


class verifyMessageView:
	def GET(self):        
		return render.signmsg()

	def POST(self):
		try:
			values = web.input(address={},signature={},message={})
			verified = verifyMessage(values['address'], values['signature'], values['message'])
		except Exception as e:
			return json.dumps(
				{
					'error': True,
					'message': str(e),
					'verified': False,
				})
		return json.dumps(
			{
				'error': False,
				'message': '',
				'verified': verified,
			})


class symmetricEncryptView:
	def GET(self):
		return render.symEncrypt("")

	def POST(self):
		formToCipher = web.input(path={}, key={}, value={})
		try:
			value_ciphered = cipherKeyValue(formToCipher['path'], formToCipher['key'].encode(), formToCipher['value'].encode(), masterkey)
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
				'valueCiphered': value_ciphered.decode(),
			})


class symmetricDecryptView:
	def POST(self):
		formToDecipher = web.input(path={}, key={}, value={})
		try:
			print("--->>> ", formToDecipher)
			value_deciphered = decipherKeyValue(formToDecipher['path'], formToDecipher['key'].encode(), formToDecipher['value'].encode(), masterkey)
			print("--->>> ", value_deciphered)
		except Exception as e:
			print("--->>> ", e)
			return json.dumps(
				{
					'error': True,
					'message': str(e),
				}) 		
		return json.dumps(
			{
				'error': False,
				'message': '',
				'valueDeciphered': value_deciphered.decode(),
			})


class bip32View:
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


class derivationView:        
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

