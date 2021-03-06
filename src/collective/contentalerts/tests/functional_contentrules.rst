.. -*- coding: utf-8 -*-

=============
Content rules
=============

Test setup
==========
    >>> from email import message_from_string
    >>> from plone.testing.z2 import Browser

    >>> app = layer['app']
    >>> portal = layer['portal']
    >>> mailhost = portal.MailHost

    >>> portal_url = portal.absolute_url()

Browser
-------
    >>> browser = Browser(app)
    >>> browser.handleErrors = False
    >>> browser.addHeader('Authorization', 'Basic admin:secret')

Add a content rule
------------------
Create a content rule::
    >>> browser.open(portal_url)
    >>> browser.getLink('Site Setup').click()
    >>> browser.getLink('Content Rules').click()
    >>> browser.getControl('Add content rule').click()
    >>> browser.getControl('Title').value = 'Test stop words'
    >>> browser.getControl('Triggering event').value = ['Object added to this container']
    >>> browser.getControl('Save').click()

Add the text alert condition::
    >>> browser.getControl('Add condition').value = ['collective.contentalerts.TextAlert']
    >>> browser.getControl('Add', index=1).click()
    >>> browser.getControl(name='form.stop_words').value = u'alert one\nalert two'
    >>> browser.getControl('Save').click()

Add a mail action::
    >>> browser.getControl('Add action').value = ['plone.actions.Mail']
    >>> browser.getControl('Add', index=3).click()
    >>> browser.getControl(name='form.subject').value = u'alert'
    >>> browser.getControl(name='form.source').value = u'plone@plone.org'
    >>> browser.getControl(name='form.recipients').value = u'moderator@plone.org'
    >>> browser.getControl(name='form.message').value = u'${text_alert}'
    >>> browser.getControl('Save').click()

Apply to the root folder::
    >>> browser.getLink('Home').click()
    >>> browser.getLink('Rules').click()
    >>> browser.getControl('Add').click()

Stop words
==========
An email is sent if a document contains certain stop words.

Add a document::
    >>> browser.getLink('Home').click()
    >>> browser.getLink('Page').click()
    >>> browser.getControl(name='title').value = u'my title'
    >>> browser.getControl(name='text').value = u'alert one here alert two there'
    >>> browser.getControl('Save').click()

An email is generated::
    >>> mail = message_from_string(mailhost.messages[0])
    >>> mail['To'] == 'moderator@plone.org'
    True
    >>> subject = mail['Subject']
    >>> 'alert' in subject
    True
    >>> message = mail.get_payload()
    >>> 'alert one' in message
    True
