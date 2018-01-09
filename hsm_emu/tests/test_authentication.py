#!/usr/bin/env python3
import unittest
from urllib.parse import urlparse
from context import (getChallengeHidden, getChallengeVisual, 
	checkPath, signAuth, verifyAuth, x, b2x)

masterkey = "tprv8ZgxMBicQKsPf4wpV8MBx9Ux4T7Cvnojkw6WMsKF6WQSTb76AinSxfjAC73f8GXZgfTczrE2U1sh2L8HJeyhbaBbjCmkdsTAAueN9HQsyvF"
path = "m/2147483661/3871070425/3772234360/3398564572/3597033557"
address = "mkcuRYXhBb6Pg8jjXuGSbfTXCJBrHPSp4d"
challenge_visual = "2018-01-09 11:27:11.038277"
challenge_hidden = "0fff787491701051326966ebd710c5fe1b4aa97dbf4bf0f72fb5a2d3117a9666"
sign_message = "487a4f586c475361362f4d704975412b3965616e6243724b5350724168632f565269485932792b7747346d38463153567831506c44584542424c4d414f53576b2b59534b7a52742f6d6574794c763242594b7934677a6f3d"

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
