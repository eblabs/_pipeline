import packages
import sys

testFunc = packages.importPackage('tests.testFunc', reloadPackage=True)

def reloadTest():
	testFunc.testFunc()