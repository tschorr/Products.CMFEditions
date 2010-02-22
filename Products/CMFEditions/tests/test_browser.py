from Products.Five.testbrowser import Browser
from Products.Five import zcml
from Products.PloneTestCase import PloneTestCase
from Products.PloneTestCase.setup import portal_owner, default_password
from Products.PloneTestCase.layer import PloneSite
from Testing import ZopeTestCase as ztc
import pkg_resources

try:
    pkg_resources.get_distribution('collective.indexing')
    has_indexing = True
except pkg_resources.DistributionNotFound:
    has_indexing = False

import unittest

class CMFEditionsBrowserLayer(PloneSite):
    @classmethod
    def setUp(cls):
        if has_indexing:
            import collective.indexing
            zcml.load_config('configure.zcml', collective.indexing)
            ztc.installPackage('collective.indexing')

    @classmethod
    def tearDown(cls):
        pass

class TestBrowserActions(PloneTestCase.FunctionalTestCase):
    layer = CMFEditionsBrowserLayer

    def getBrowser(self):
        browser = Browser()
        browser.open(self.portal.absolute_url())
        browser.getControl(name='__ac_name').value = portal_owner
        browser.getControl(name='__ac_password').value = default_password
        browser.getControl(name='submit').click()
        return browser

    def testAddingFileAndSavingIt(self):
        br = self.getBrowser()
        br.getLink('Page').click()
        br.getControl(name='title').value = 'title v1'
        br.getControl(name='cmfeditions_version_comment').value = 'comment v1'
        br.getControl('Save').click()
        for i in ['2', '3']:
            br.getLink('Edit').click()
            br.getControl(name='title').value = 'title v' + i
            br.getControl(name='cmfeditions_version_comment').value =\
                'comment v' + i
            br.getControl('Save').click()
        self.failUnless('title v3' in br.contents)
        self.failIf('title v2' in br.contents)
        self.failIf('title v1' in br.contents)
        self.failUnless('comment v3' in br.contents)
        self.failUnless('comment v2' in br.contents)
        self.failUnless('comment v1' in br.contents)

    def testAddingFileAndSavingItWithIndexing(self):
        if has_indexing:
            self.portal.portal_quickinstaller.installProduct('collective.indexing')
            self.testAddingFileAndSavingIt()
            self.portal.portal_quickinstaller.uninstallProducts(['collective.indexing'])
        else:
            pass
