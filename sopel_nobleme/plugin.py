"""Nobleme Plugin for Sopel"""
from __future__ import annotations

import json
from typing import TYPE_CHECKING
from urllib.parse import urljoin

import requests
from sopel import plugin

if TYPE_CHECKING:
    from sopel.bot import SopelWrapper
    from sopel.trigger import Trigger


NOBLEME_BASE_URL = 'https://nobleme.com/'
NOBLEME_QUOTES_URL = urljoin(NOBLEME_BASE_URL, '/pages/quotes')
NOBLEME_QUOTES_API = urljoin(NOBLEME_BASE_URL, '/api/quotes')
NOBLEME_QUOTE_ID_API = urljoin(NOBLEME_BASE_URL, '/api/quote')


@plugin.commands('quote', 'q')
@plugin.output_prefix('[Quote] ')
def command(bot: SopelWrapper, trigger: Trigger) -> None:
    """Fetch a quote from the Nobleme API and reply with an URL."""
    quote_number: str | None = trigger.group(2)
    if not quote_number:
        bot.reply(
            'miscellanea are available online at %s' % NOBLEME_QUOTES_URL)
        return

    if not quote_number.isnumeric():
        bot.reply(
            'Not a quote number, miscellanea are available online at %s'
            % NOBLEME_QUOTES_URL
        )
        return

    response = requests.get(NOBLEME_QUOTE_ID_API + '/' + quote_number)

    if response.status_code == 200:
        data = json.loads(response.text)
        quote = data.get('quote', {})

        if not quote:
            bot.reply('Quote "%s" not found' % quote_number)
            return

    else:
        bot.reply('Quote "%s" not found.' % quote_number)
        return

    # extract quote's attributes
    is_nsfw: bool = bool(quote.get('is_nsfw', False))
    texts: list[str] = quote.get('body', '').splitlines()
    url: str = quote.get('link', '')
    is_too_long: bool = len(texts) > 2

    # format end message
    template: str = 'Read online: {url}'

    # abstract if SFW, URL only otherwise
    if is_nsfw:
        # add the NSFW tag but do not send any abstract
        template = 'Read online (NSFW): {url}'
    else:
        # check quote length
        if is_too_long:
            template = 'Read full quote: {url}'

        # send abstract
        for text in texts[:2]:
            bot.say(text.strip(), truncation='[…]')

    # send final message with quote's link
    bot.say(
        template.format(**{
            'url': url,
        })
    )

    return
