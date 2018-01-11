#!/usr/bin/env python3
import sys
if sys.version_info.major < 3:
	sys.stderr.write('Sorry, Python 3.x required by this example.\n')
	sys.exit(1)

import unittest
from urllib.parse import urlparse
from context import (getChallengeHidden, getChallengeVisual, 
	checkPath, signAuth, verifyAuth, x, b2x)

masterkey = "tprv8ZgxMBicQKsPf4wpV8MBx9Ux4T7Cvnojkw6WMsKF6WQSTb76AinSxfjAC73f8GXZgfTczrE2U1sh2L8HJeyhbaBbjCmkdsTAAueN9HQsyvF"
path = "m/2147483661/3871070425/3772234360/3398564572/3597033557"
address = "mrRXNQEvCyajiUhkSmYHSk7aeqsJuXnxLt"
challenge_visual = "2018-01-09 11:27:11.038277"
challenge_hidden = "0fff787491701051326966ebd710c5fe1b4aa97dbf4bf0f72fb5a2d3117a9666"
sign_message = "49507a45587145784a53346c6a5962744963565764444e527347306c3654756b343032515038657a3355782b50356c574d735450397775754d2f2b516478785049306153384931713555345438333168707a582f7173413d"

class TestAuth(unittest.TestCase):
	def test_path_success(self):		
		url = urlparse('http://satoshi@bitcoin.org:8080/login?1')
		hdkeypath = checkPath(url)

		self.assertEqual(hdkeypath, path)

	def test_fail_challenge_visual(self):
		challen_1 = getChallengeVisual()
		self.assertNotEqual(challen_1, getChallengeVisual())

	def test_fail_challenge_hidden(self):
		challen_1 = getChallengeHidden()
		self.assertNotEqual(challen_1, getChallengeHidden())

	def test_verify_auth_success(self):
		is_verify = verifyAuth(challenge_hidden, challenge_visual, address, x(sign_message))
		self.assertTrue(is_verify)

	def test_sign_verify_success(self):
		challen_visual = getChallengeVisual()
		challen_hidden = getChallengeHidden()
		sign_msg = signAuth(challen_hidden, challen_visual, path)

		self.assertNotEqual(challen_hidden, challenge_hidden)
		self.assertNotEqual(challen_visual, challenge_visual)
		self.assertEqual(str(sign_msg[0]), address)
		self.assertNotEqual(b2x(sign_msg[1]), sign_message)

		is_verify = verifyAuth(challen_hidden, challen_visual, address, sign_msg[1])
		self.assertTrue(is_verify)

if __name__ == '__main__':
	unittest.main()
