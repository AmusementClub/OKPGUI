# coding=utf-8

from configparser import RawConfigParser
from html.parser import HTMLParser
from collections import defaultdict
from os.path import join, dirname


class Attributes(dict):
    def __getitem__(self, name):
        try:
            return super(Attributes, self).__getitem__(name)
        except KeyError:
            return ''


class ConfigParser(RawConfigParser, object):
    def get(self, section, option):
        value = super(ConfigParser, self).get(section, option)
        return value.replace('\\n', '\n')


class HTML2BBCode(HTMLParser):
    """
    HTML to BBCode converter

    >>> parser = HTML2BBCode()
    >>> str(parser.feed('<ul><li>one</li><li>two</li></ul>'))
    '[list][li]one[/li][li]two[/li][/list]'

    >>> str(parser.feed('<a href="http://google.com/">Google</a>'))
    '[url=http://google.com/]Google[/url]'

    >>> str(parser.feed('<img src="http://www.google.com/images/logo.png">'))
    '[img]http://www.google.com/images/logo.png[/img]'

    >>> str(parser.feed('<em>EM test</em>'))
    '[i]EM test[/i]'

    >>> str(parser.feed('<strong>Strong text</strong>'))
    '[b]Strong text[/b]'

    >>> str(parser.feed('<code>a = 10;</code>'))
    '[code]a = 10;[/code]'

    >>> str(parser.feed('<blockquote>Beautiful is better than ugly.</blockquote>'))
    '[quote]Beautiful is better than ugly.[/quote]'

    >>> str(parser.feed('<font face="Arial">Text decorations</font>'))
    '[font=Arial]Text decorations[/font]'

    >>> str(parser.feed('<font size="2">Text decorations</font>'))
    '[size=2]Text decorations[/size]'

    >>> str(parser.feed('<font color="red">Text decorations</font>'))
    '[color=red]Text decorations[/color]'

    >>> str(parser.feed('<font face="Arial" color="green" size="2">Text decorations</font>'))
    '[color=green][font=Arial][size=2]Text decorations[/size][/font][/color]'

    >>> str(parser.feed('Text<br>break'))
    'Text\\nbreak'

    >>> str(parser.feed('&nbsp;'))
    '&nbsp;'
    """

    def __init__(self, config=None):
        HTMLParser.__init__(self)
        self.config = ConfigParser(allow_no_value=True)
        self.config.read(join(dirname(__file__), 'data/defaults.conf'))
        if config:
            self.config.read(config)

    def handle_starttag(self, tag, attrs):
        if self.config.has_section(tag):
            self.attrs[tag].append(dict(attrs))
            self.data.append(
                self.config.get(tag, 'start') % Attributes(attrs or {}))
            if self.config.has_option(tag, 'expand'):
                self.expand_starttags(tag)

    def handle_endtag(self, tag):
        if self.config.has_section(tag):
            self.data.append(self.config.get(tag, 'end'))
            if self.config.has_option(tag, 'expand'):
                self.expand_endtags(tag)
            self.attrs[tag].pop()

    def handle_data(self, data):
        self.data.append(data)

    def feed(self, data):
        self.data = []
        self.attrs = defaultdict(list)
        HTMLParser.feed(self, data)
        return ''.join(self.data)

    def expand_starttags(self, tag):
        for expand in self.get_expands(tag):
            if expand in self.attrs[tag][-1]:
                self.data.append(
                    self.config.get(expand, 'start') % self.attrs[tag][-1])

    def expand_endtags(self, tag):
        for expand in reversed(self.get_expands(tag)):
            if expand in self.attrs[tag][-1]:
                self.data.append(
                    self.config.get(expand, 'end') % self.attrs[tag][-1])

    def get_expands(self, tag):
        expands = self.config.get(tag, 'expand').split(',')
        return [x.strip() for x in expands]

    def handle_entityref(self, name):
        self.data.append('&{};'.format(name))

    def handle_charref(self, name):
        self.data.append('&#{};'.format(name))


if __name__ == '__main__':
    import doctest

    doctest.testmod()
