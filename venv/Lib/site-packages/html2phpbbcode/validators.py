import regex

"""The following validators have been based on phpBB's URL and e-mail validators, which are available under GNU GPL v2.0 license.

Link: https://github.com/phpbb/area51-phpbb3/blob/master/phpBB/includes/functions.php

Copyright notice as found in phpBB:

/**
*
* phpBB © Copyright phpBB Limited 2003-2016
* http://www.phpbb.com
*
* phpBB is free software. You can redistribute it and/or modify it
* under the terms of the GNU General Public License, version 2 (GPL-2.0)
* as published by the Free Software Foundation.
*
* This program is distributed in the hope that it will be useful,
* but WITHOUT ANY WARRANTY; without even the implied warranty of
* MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
* GNU General Public License for more details.
*
* A copy of the license can be viewed in the docs/LICENSE.txt file.
* The same can be viewed at <http://opensource.org/licenses/gpl-2.0.php>
*
*/

"""

url = [
    regex.compile(
        r"[a-z][a-z\d+\-.]*(?<!javascript):/{2}(?:(?:[^\p{C}\p{Z}\p{S}\p{P}\p{Nl}\p{No}\p{Me}\u1100-\u115F\uA960-\uA97C\u1160-\u11A7\uD7B0-\uD7C6\u20D0-\u20FF\U0001D100-\U0001D1FF\U0001D200-\U0001D24F\u0640\u07FA\u302E\u302F\u3031-\u3035\u303B]*[\u00B7\u0375\u05F3\u05F4\u30FB\u002D\u06FD\u06FE\u0F0B\u3007\u00DF\u03C2\u200C\u200D\pL0-9\-._~!$&'()*+,;=:@|]+|%[\dA-F]{2})+|[0-9.]+|\[[a-z0-9.]+:[a-z0-9.]+:[a-z0-9.:]+\])(?::\d*)?(?:/(?:[^\p{C}\p{Z}\p{S}\p{P}\p{Nl}\p{No}\p{Me}\u1100-\u115F\uA960-\uA97C\u1160-\u11A7\uD7B0-\uD7C6\u20D0-\u20FF\U0001D100-\U0001D1FF\U0001D200-\U0001D24F\u0640\u07FA\u302E\u302F\u3031-\u3035\u303B]*[\u00B7\u0375\u05F3\u05F4\u30FB\u002D\u06FD\u06FE\u0F0B\u3007\u00DF\u03C2\u200C\u200D\pL0-9\-._~!$&'()*+,;=:@|]+|%[\dA-F]{2})*)*(?:\?(?:[^\p{C}\p{Z}\p{S}\p{P}\p{Nl}\p{No}\p{Me}\u1100-\u115F\uA960-\uA97C\u1160-\u11A7\uD7B0-\uD7C6\u20D0-\u20FF\U0001D100-\U0001D1FF\U0001D200-\U0001D24F\u0640\u07FA\u302E\u302F\u3031-\u3035\u303B]*[\u00B7\u0375\u05F3\u05F4\u30FB\u002D\u06FD\u06FE\u0F0B\u3007\u00DF\u03C2\u200C\u200D\pL0-9\-._~!$&'()*+,;=:@/?|]+|%[\dA-F]{2})*)?(?:\#(?:[^\p{C}\p{Z}\p{S}\p{P}\p{Nl}\p{No}\p{Me}\u1100-\u115F\uA960-\uA97C\u1160-\u11A7\uD7B0-\uD7C6\u20D0-\u20FF\U0001D100-\U0001D1FF\U0001D200-\U0001D24F\u0640\u07FA\u302E\u302F\u3031-\u3035\u303B]*[\u00B7\u0375\u05F3\u05F4\u30FB\u002D\u06FD\u06FE\u0F0B\u3007\u00DF\u03C2\u200C\u200D\pL0-9\-._~!$&'()*+,;=:@/?|]+|%[\dA-F]{2})*)?",
        regex.UNICODE | regex.IGNORECASE
    ),
    regex.compile(
        r"www\.(?:[^\p{C}\p{Z}\p{S}\p{P}\p{Nl}\p{No}\p{Me}\u1100-\u115F\uA960-\uA97C\u1160-\u11A7\uD7B0-\uD7C6\u20D0-\u20FF\U0001D100-\U0001D1FF\U0001D200-\U0001D24F\u0640\u07FA\u302E\u302F\u3031-\u3035\u303B]*[\u00B7\u0375\u05F3\u05F4\u30FB\u002D\u06FD\u06FE\u0F0B\u3007\u00DF\u03C2\u200C\u200D\pL0-9\-._~!$&'()*+,;=:@|]+|%[\dA-F]{2})+(?::\d*)?(?:/(?:[^\p{C}\p{Z}\p{S}\p{P}\p{Nl}\p{No}\p{Me}\u1100-\u115F\uA960-\uA97C\u1160-\u11A7\uD7B0-\uD7C6\u20D0-\u20FF\U0001D100-\U0001D1FF\U0001D200-\U0001D24F\u0640\u07FA\u302E\u302F\u3031-\u3035\u303B]*[\u00B7\u0375\u05F3\u05F4\u30FB\u002D\u06FD\u06FE\u0F0B\u3007\u00DF\u03C2\u200C\u200D\pL0-9\-._~!$&'()*+,;=:@|]+|%[\dA-F]{2})*)*(?:\?(?:[^\p{C}\p{Z}\p{S}\p{P}\p{Nl}\p{No}\p{Me}\u1100-\u115F\uA960-\uA97C\u1160-\u11A7\uD7B0-\uD7C6\u20D0-\u20FF\U0001D100-\U0001D1FF\U0001D200-\U0001D24F\u0640\u07FA\u302E\u302F\u3031-\u3035\u303B]*[\u00B7\u0375\u05F3\u05F4\u30FB\u002D\u06FD\u06FE\u0F0B\u3007\u00DF\u03C2\u200C\u200D\pL0-9\-._~!$&'()*+,;=:@/?|]+|%[\dA-F]{2})*)?(?:\#(?:[^\p{C}\p{Z}\p{S}\p{P}\p{Nl}\p{No}\p{Me}\u1100-\u115F\uA960-\uA97C\u1160-\u11A7\uD7B0-\uD7C6\u20D0-\u20FF\U0001D100-\U0001D1FF\U0001D200-\U0001D24F\u0640\u07FA\u302E\u302F\u3031-\u3035\u303B]*[\u00B7\u0375\u05F3\u05F4\u30FB\u002D\u06FD\u06FE\u0F0B\u3007\u00DF\u03C2\u200C\u200D\pL0-9\-._~!$&'()*+,;=:@/?|]+|%[\dA-F]{2})*)?",
        regex.UNICODE | regex.IGNORECASE
    )
]

mail = [
    regex.compile(
        r"((?:[\w\!\#$\%\&\'\*\+\-\/\=\?\^\`{\|\}\~]+\.)*(?:[\w\!\#$\%\'\*\+\-\/\=\?\^\`{\|\}\~]|&amp;)+)@((((([a-z0-9]{1}[a-z0-9\-]{0,62}[a-z0-9]{1})|[a-z])\.)+[a-z]{2,63})|(\d{1,3}\.){3}\d{1,3}(\:\d{1,5})?)",
        regex.IGNORECASE
    )
]

def is_valid_url(subject):
    return any((u.match(subject) for u in url))

def is_valid_mail(subject):
    return any((m.match(subject) for m in mail))