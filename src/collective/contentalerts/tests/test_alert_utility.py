# -*- coding: utf-8 -*-
from collective.contentalerts.interfaces import IAlert
from collective.contentalerts.interfaces import IStopWords
from collective.contentalerts.testing import COLLECTIVE_CONTENTALERTS_INTEGRATION_TESTING  # noqa
from collective.contentalerts.utilities import Alert
from plone.registry.interfaces import IRegistry
from zope.component import getUtility

import unittest


class AlertUtilityTestCase(unittest.TestCase):
    layer = COLLECTIVE_CONTENTALERTS_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']

        self.registry = getUtility(IRegistry)
        self.records = self.registry.forInterface(IStopWords)
        self.utility = getUtility(IAlert)

    def test_utility_exists(self):
        self.assertTrue(self.utility)

    def test_no_registry_no_error(self):
        """Check that if the registry does not work the utility handles it."""
        # delete the record on the registry
        key = self.records.__schema__.__identifier__ + '.stop_words'
        del self.registry.records[key]

        self.assertIsNone(self.utility._get_registry_stop_words())

    def test_empty_registry_no_error(self):
        self.records.stop_words = u''
        self.assertEqual(
            self.utility.get_snippets(u'some random text'),
            u''
        )

    def test_has_words_from_empty_registry(self):
        """Check that if the registry is empty has_stop_words returns False."""
        self.records.stop_words = u''
        self.assertFalse(
            self.utility.has_stop_words(u'some random text')
        )

    def test_has_words_from_registry(self):
        """Check that has_stop_words works with the registry."""
        self.records.stop_words = u'random\nalert me\nlala'
        self.assertTrue(
            self.utility.has_stop_words(u'some random text')
        )

    def test_no_has_words_from_registry(self):
        """Check that has_stop_words works with the registry."""
        self.records.stop_words = u'random\nalert me\nlala'
        self.assertFalse(
            self.utility.has_stop_words(u'some specific text')
        )

    def test_get_snippets_from_registry(self):
        """Check that get_snippets works with the registry."""
        self.records.stop_words = u'random\nalert me\nlala'
        self.assertEqual(
            self.utility.get_snippets(u'some random text', chars=2),
            u'random\n\n...e random t...'
        )

    def test_no_get_snippets_from_registry(self):
        """Check that get_snippets works with the registry."""
        self.records.stop_words = u'random\nalert me\nlala'
        self.assertEqual(
            self.utility.get_snippets(u'some specific text'),
            u''
        )


class HTMLNormalizeTestCase(unittest.TestCase):

    def setUp(self):
        self.normalize = Alert.html_normalize

    def test_regular_text_left_as_is(self):
        text = u'normal text'
        self.assertEqual(self.normalize(text), text)

    def test_lower_case(self):
        text = u'UAU'
        self.assertEqual(self.normalize(text), u'uau')

    def test_unicode_normalized_form(self):
        text = u'älert'
        self.assertEqual(self.normalize(text), u'alert')

    def test_unicode_normalized_form_lower_case(self):
        text = u'Älert'
        self.assertEqual(self.normalize(text), u'alert')

    def test_html_entity(self):
        text = u'alert&#220;s'
        self.assertEqual(self.normalize(text), u'alertus')

    def test_html_entity_lower_case(self):
        text = u'alert&#252;s'
        self.assertEqual(self.normalize(text), u'alertus')

    def test_multiple_spaces_on_source(self):
        text = u'alert     text'
        self.assertEqual(self.normalize(text), u'alert text')

    def test_string(self):
        text = 'some string'
        self.assertEqual(self.normalize(text), text)

    def test_string_umlauts(self):
        text = 'some \xfc'
        self.assertEqual(self.normalize(text), u'some u')


class SnippetTestCase(unittest.TestCase):

    def setUp(self):
        self.snippet = Alert._snippet

    def test_snippet_is_returned(self):
        text = u'normal text with more '
        self.assertEqual(
            self.snippet(text, text.find('text'), 'text', 3),
            '\n\n...al text wi...'
        )

    def test_padding(self):
        text = u'normal text with more'
        self.assertEqual(
            self.snippet(text, text.find('text'), 'text', 5),
            '\n\n...rmal text with...'
        )

    def test_more_padding_than_text(self):
        text = u'normal text with more'
        self.assertEqual(
            self.snippet(text, text.find('text'), 'text', 150),
            '\n\n...normal text with more...'
        )

    def test_text_at_the_end(self):
        text = u'normal text'
        self.assertEqual(
            self.snippet(text, text.find('text'), 'text', 2),
            '\n\n...l text...'
        )

    def test_text_at_the_beginning(self):
        text = u'normal text'
        self.assertEqual(
            self.snippet(text, text.find('text'), 'text', 2),
            '\n\n...l text...'
        )


class UniqueTestCase(unittest.TestCase):

    def setUp(self):
        self.unique = Alert._unique

    def test_no_dups_same_list(self):
        elements = ('a', 'b', )
        self.assertEqual(len(self.unique(elements)), len(elements))

    def test_only_unique(self):
        elements = ('a', 'b', 'a', )
        unique = self.unique(elements)
        self.assertEqual(unique, ['a', 'b'])


class GetSnippetsTestCase(unittest.TestCase):

    def setUp(self):
        self.snippets = Alert().get_snippets

    def test_no_text(self):
        text = None
        stop_words = u'one\ntwo'
        self.assertEqual(self.snippets(text, stop_words), u'')

    def test_empty_text(self):
        text = u''
        stop_words = u'one\ntwo'
        self.assertEqual(self.snippets(text, stop_words), u'')

    def test_no_stop_word_in_text(self):
        text = u'Random normal text'
        stop_words = u'one\ntwo'
        self.assertEqual(self.snippets(text, stop_words), u'')

    def test_stop_word_in_text(self):
        text = u'Alerts two text'
        stop_words = u'one\ntwo'
        snippet_text = self.snippets(text, stop_words, chars=1)
        self.assertEqual(snippet_text, u'two\n\n... two ...')

    def test_unicode_text(self):
        text = u'Alerts twö text'
        stop_words = u'one\ntwo'
        snippet_text = self.snippets(text, stop_words, chars=3)
        self.assertEqual(snippet_text, u'two\n\n...ts two te...')

    def test_multiple_stop_words(self):
        text = u'Alerts one text and two more text'
        stop_words = u'one\ntwo'
        snippet_text = self.snippets(text, stop_words, chars=1)
        self.assertEqual(
            snippet_text,
            u'one, two\n\n... one ...\n\n... two ...'
        )

    def test_different_line_endings(self):
        text = u'and one alert or second alert and even third alert on text'
        stop_words = u'one alert\r\nsecond alert\nthird alert'
        snippet_text = self.snippets(text, stop_words, chars=2)
        self.assertEqual(
            snippet_text,
            u'one alert, second alert, third alert'
            u'\n\n...d one alert o...'
            u'\n\n...r second alert a...'
            u'\n\n...n third alert o...'
        )

    def test_ignore_empty_lines(self):
        text = u'and one alert or text'
        stop_words = u'one alert\n\n\n\nsecond alert\nthird alert'
        snippet_text = self.snippets(text, stop_words, chars=2)
        self.assertEqual(
            snippet_text,
            u'one alert\n\n...d one alert o...'
        )

    def test_same_stop_word_more_than_once(self):
        text = u'Alerts one text and one more text'
        stop_words = u'one\ntwo'
        snippet_text = self.snippets(text, stop_words, chars=3)
        self.assertEqual(
            snippet_text,
            u'one\n\n...ts one te...\n\n...nd one mo...'
        )

    def test_keep_text_in_order(self):
        """Show the snippets in the order they appear on the text.

        In this text the stop words are 'one' and 'two' and in the text 'two'
        is the first to be show up, thus a normal iteration over the text would
        report 'one' first and then 'two', which is the other way around on the
        text.
        """
        text = u'Alerts two text and one more text'
        stop_words = u'one\ntwo'
        snippet_text = self.snippets(text, stop_words, chars=3)
        self.assertEqual(
            snippet_text,
            u'two, one\n\n...ts two te...\n\n...nd one mo...'
        )

    def test_keep_text_in_order_multiple_occurrences(self):
        text = u'Alerts two text and one more text and some more two tired'
        stop_words = u'one\ntwo'
        snippet_text = self.snippets(text, stop_words, chars=2)
        self.assertEqual(
            snippet_text,
            u'two, one\n\n...s two t...\n\n...d one m...\n\n...e two t...'
        )


class HasStopWordsTestCase(unittest.TestCase):

    def setUp(self):
        self.has_words = Alert().has_stop_words

    def test_no_text(self):
        text = None
        stop_words = u'one\ntwo'
        self.assertFalse(self.has_words(text, stop_words))

    def test_empty_text(self):
        text = u''
        stop_words = u'one\ntwo'
        self.assertFalse(self.has_words(text, stop_words))

    def test_no_stop_word_in_text(self):
        text = u'Random normal text'
        stop_words = u'one\ntwo'
        self.assertFalse(self.has_words(text, stop_words))

    def test_stop_word_in_text(self):
        text = u'Alerts two text'
        stop_words = u'one\ntwo'
        self.assertTrue(self.has_words(text, stop_words))
