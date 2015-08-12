# -*- coding: utf-8 -*-
"""Module where all interfaces, events and exceptions live."""
from collective.contentalerts import _
from zope import schema
from zope.interface import Interface


class ICollectiveContentalertsLayer(Interface):
    """Marker interface that defines a browser layer."""


class IStopWords(Interface):

    stop_words = schema.Text(
        title=_(
            u'settings_stop_words_list_title',
            default=u'List'
        ),
        description=_(
            u'settings_stop_words_list_description',
            default=u'Words/sentences that will generate an alert, '
                    u'one per line.'
        ),
        required=False,
    )


class IAlert(Interface):
    """Utility to know if a given text contains suspicious text."""

    def get_snippets(text, stop_words=None, chars=150):
        """Returns the stop words found in the text surrounded by some text.

        :param text: where stop words will be searched on.
        :type text: str
        :param chars: how many surrounding characters should be shown around
            a stop word.
        :type chars: int
        :param stop_words: list of words that will be searched on the text.
            If not provided the default.
        :type stop_words: list
        :returns: formatted text with a list of the stop words found and the
          snippets below them.
        :rtype: str
        """

    def has_stop_words(text, stop_words=None):
        """Checks if the given text has words from the provided stop words.

        :param text: where stop words will be searched on.
        :type text: str
        :param stop_words: list of words that will be searched on the text.
        :type stop_words: list
        :returns: whether the text contains words from the stop words.
        :rtype: bool
        """
