# -*- coding: utf-8 -*-
from collective.contentalerts.contentrules import TextAlertCondition
from collective.contentalerts.contentrules import TextAlertConditionEditForm
from collective.contentalerts.interfaces import IStopWords
from collective.contentalerts.testing import COLLECTIVE_CONTENTALERTS_INTEGRATION_TESTING  # noqa
from plone.app.contentrules.rule import Rule
from plone.app.discussion.interfaces import IConversation
from plone.app.testing import TEST_USER_ID
from plone.app.testing import setRoles
from plone.contentrules.engine.interfaces import IRuleStorage
from plone.contentrules.rule.interfaces import IExecutable
from plone.contentrules.rule.interfaces import IRuleCondition
from plone.registry.interfaces import IRegistry
from zope.component import createObject
from zope.component import getMultiAdapter
from zope.component import getUtility
from zope.component.interfaces import IObjectEvent
from zope.interface import implementer

import unittest


@implementer(IObjectEvent)
class CommentDummyEvent(object):

    def __init__(self, obj):
        self.comment = obj


class TextAlertConditionTestCase(unittest.TestCase):
    layer = COLLECTIVE_CONTENTALERTS_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        self.registry = getUtility(IRegistry)
        setRoles(self.portal, TEST_USER_ID, ['Manager'])

        self.name = 'collective.contentalerts.TextAlert'
        self.element = getUtility(
            IRuleCondition,
            name=self.name
        )

        name = self.portal.invokeFactory(
            id='doc1',
            title='Document 1',
            type_name='Document'
        )

        self.document = self.portal[name]

        registry = getUtility(IRegistry)
        self.records = registry.forInterface(IStopWords)

    def _add_comment(self, text):
        comment = createObject('plone.Comment')
        comment.text = text
        comment.author_username = 'jim'
        comment.author_name = 'Jim'
        comment.author_email = 'jim@example.com'
        conversation = IConversation(self.document)
        conversation.addComment(comment)
        return comment

    def test_registered(self):
        self.assertEqual(self.name, self.element.addview)
        self.assertEqual('edit', self.element.editview)
        self.assertEqual(None, self.element.for_)
        self.assertEqual(IObjectEvent, self.element.event)

    def test_add_view_no_data(self):
        storage = getUtility(IRuleStorage)
        storage[u'foo'] = Rule()
        rule = self.portal.restrictedTraverse('++rule++foo')

        adding = getMultiAdapter(
            (rule, self.portal.REQUEST),
            name='+condition'
        )
        add_view = getMultiAdapter(
            (adding, self.portal.REQUEST),
            name=self.element.addview
        )

        add_view.createAndAdd(data={})

        condition = rule.conditions[0]
        self.assertTrue(isinstance(condition, TextAlertCondition))
        self.assertEqual(condition.stop_words, None)

    def test_add_view_with_stop_words(self):
        stop_words = u'alert\nanother alert\nlast one'
        storage = getUtility(IRuleStorage)
        storage[u'foo'] = Rule()
        rule = self.portal.restrictedTraverse('++rule++foo')

        adding = getMultiAdapter(
            (rule, self.portal.REQUEST),
            name='+condition'
        )
        add_view = getMultiAdapter(
            (adding, self.portal.REQUEST),
            name=self.element.addview
        )

        add_view.createAndAdd(data={'stop_words': stop_words})

        condition = rule.conditions[0]
        self.assertTrue(isinstance(condition, TextAlertCondition))
        self.assertEqual(
            condition.stop_words,
            stop_words
        )

    def test_edit_view(self):
        condition = TextAlertCondition()
        edit_view = getMultiAdapter(
            (condition, self.request),
            name=self.element.editview
        )
        self.assertTrue(
            isinstance(edit_view, TextAlertConditionEditForm)
        )

    def test_empty_text_no_condition(self):
        comment = self._add_comment('')
        condition = TextAlertCondition()

        executable = getMultiAdapter(
            (self.portal, condition, CommentDummyEvent(comment)),
            IExecutable
        )
        self.assertFalse(executable())

    def test_no_text_no_condition(self):
        comment = self._add_comment(None)
        condition = TextAlertCondition()

        executable = getMultiAdapter(
            (self.portal, condition, CommentDummyEvent(comment)),
            IExecutable
        )
        self.assertFalse(executable())

    def test_regular_text_no_local_no_registry_stop_words(self):
        comment = self._add_comment('regular text')
        condition = TextAlertCondition()

        self.assertEqual(self.records.stop_words, None)
        self.assertEqual(condition.stop_words, None)

        executable = getMultiAdapter(
            (self.portal, condition, CommentDummyEvent(comment)),
            IExecutable
        )
        self.assertFalse(executable())

    def test_regular_text_no_local_stop_words_and_registry_stop_words(self):
        comment = self._add_comment('regular text')
        condition = TextAlertCondition()

        self.assertEqual(self.records.stop_words, None)
        condition.stop_words = u'one alert\nanother alert'

        executable = getMultiAdapter(
            (self.portal, condition, CommentDummyEvent(comment)),
            IExecutable
        )
        self.assertFalse(executable())

    def test_regular_text_local_stop_words_and_no_registry_stop_words(self):
        comment = self._add_comment('regular text')
        condition = TextAlertCondition()

        self.records.stop_words = u'one alert\nanother alert'
        self.assertEqual(condition.stop_words, None)

        executable = getMultiAdapter(
            (self.portal, condition, CommentDummyEvent(comment)),
            IExecutable
        )
        self.assertFalse(executable())

    def test_regular_text_local_and_registry_stop_words(self):
        comment = self._add_comment('regular text')
        condition = TextAlertCondition()

        self.records.stop_words = u'yet another\nlast one'
        condition.stop_words = u'one alert\nanother alert'

        executable = getMultiAdapter(
            (self.portal, condition, CommentDummyEvent(comment)),
            IExecutable
        )
        self.assertFalse(executable())

    def test_alert_text_no_local_stop_words_and_registry_stop_words(self):
        comment = self._add_comment('this gives one alert')
        condition = TextAlertCondition()

        self.records.stop_words = u'one alert\nanother alert'
        self.assertEqual(condition.stop_words, None)

        executable = getMultiAdapter(
            (self.portal, condition, CommentDummyEvent(comment)),
            IExecutable
        )
        self.assertTrue(executable())

    def test_alert_text_local_stop_words_no_registry_stop_words(self):
        comment = self._add_comment('this gives one alert')
        condition = TextAlertCondition()

        self.assertEqual(self.records.stop_words, None)
        condition.stop_words = u'one alert\nanother alert'

        executable = getMultiAdapter(
            (self.portal, condition, CommentDummyEvent(comment)),
            IExecutable
        )
        self.assertTrue(executable())

    def test_alert_text_local_and_registry_stop_words(self):
        comment = self._add_comment('this gives one alert')
        condition = TextAlertCondition()

        self.records.stop_words = u'almost\nlast one'
        condition.stop_words = u'one alert\nanother alert'

        executable = getMultiAdapter(
            (self.portal, condition, CommentDummyEvent(comment)),
            IExecutable
        )
        self.assertTrue(executable())

    def test_alert_text_local_stop_words_shadow_registry_stop_words(self):
        """Local stop words list shadows the registry stop words.

        This basically means that if the text contains stop words from
        the registry, but there is a local stop words list that does not
        complain, the text will be reported that it does *not* contain stop
        words.

        That's a way to override the general stop words list to provide a
        completely different set of stop words.
        """
        comment = self._add_comment('this should give one alert')
        condition = TextAlertCondition()

        self.records.stop_words = u'one alert\nanother alert'
        condition.stop_words = u'almost\nlast one'

        executable = getMultiAdapter(
            (self.portal, condition, CommentDummyEvent(comment)),
            IExecutable
        )
        self.assertFalse(executable())
