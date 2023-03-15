from os.path import join, dirname

from html2bbcode.parser import HTML2BBCode, Attributes
from .validators import is_valid_url, is_valid_mail

def is_mailto_url(url):
    return url.startswith("mailto:") and is_valid_mail(url[7:])

class HTML2PHPBBCode(HTML2BBCode):
    def __init__(self, config=None):
        if config is None:
            config = join(dirname(__file__), "data/defaults.conf")
        super().__init__(config=config)
    
    def handle_starttag(self, tag, attrs):
        if self.config.has_section(tag):
            dct = dict(attrs)

            skip = False
            if tag == "font" and "size" in dct:
                sz = dct["size"]
                if sz.isdigit() and int(sz) >= 1 and int(sz) <= 7:
                    """Size attribute of <font> tag is a number between 1-7"""
                    sz = int(100 * 1.15 ** (int(sz) - 3))
                else:
                    sz = 100
                dct["size"] = str(sz)
            if tag == "a":
                if "href" not in dct:
                    """Mark link as invalid so that handle_endtag knows to ignore it"""
                    dct["!invalid"] = True
                    skip = True
                else:
                    url = dct["href"]
                    if is_mailto_url(url):
                        """Remove mailto: from URL"""
                        attrs = {"email": url[7:]}
                        """Mark link as mail so that handle_endtag knows how to close it"""
                        dct["!mail"] = True
                        self.data.append(
                            self.config.get("email", "start") % Attributes(attrs or {})
                        )
                        skip = True
                    elif not is_valid_url(url):
                        dct["!invalid"] = True
                        skip = True

            self.attrs[tag].append(dct)
            if not skip:
                self.data.append(
                    self.config.get(tag, "start") % Attributes(attrs or {})
                )
            if self.config.has_option(tag, "expand"):
                self.expand_starttags(tag)

    def handle_endtag(self, tag):
        if self.config.has_section(tag):
            attrs = self.attrs[tag][-1]

            skip = False
            if tag == "a":
                if "!invalid" in attrs:
                    skip = True
                if "!mail" in attrs:
                    self.data.append(self.config.get("email", "end"))
                    skip = True
            
            if not skip:
                self.data.append(self.config.get(tag, "end"))
            if self.config.has_option(tag, "expand"):
                self.expand_endtags(tag)
            self.attrs[tag].pop()
    
    def handle_data(self, data):
        """Remove excessive whitespace from text nodes
        
        TODO: Use the CSS Text Module Level 3 Working Draft rules for
        inline formatting contexts to process whitespace.
        Link: https://www.w3.org/TR/css-text-3/#white-space-processing"""

        """If there is leading whitespace, replace it with a single space"""
        left = data.lstrip()
        if left != data:
            data = " " + left
        """Same for trailing whitespace"""
        right = data.rstrip()
        if right != data:
            data = right + " "
        """Replace new lines with spaces"""
        data = data.replace("\n", " ")
        self.data.append(data)
