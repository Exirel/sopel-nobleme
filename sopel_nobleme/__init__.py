"""Nobleme Plugin for Sopel"""
import json

import pkg_resources
import requests
from sopel import module

__version__ = pkg_resources.get_distribution('sopel_nobleme').version


NOBLEME_QUOTES_URL = 'https://nobleme.com/pages/quotes/'
NOBLEME_QUOTES_API = 'https://nobleme.com/api/v1/quotes'


@module.commands('quote', 'q')
def command(bot, trigger):
    """Fetch a quote from the Nobleme API and reply with an URL."""
    quote_number = trigger.group(2)
    if not quote_number:
        bot.reply(
            'miscellanea are available online at %s' % NOBLEME_QUOTES_URL)
        return

    response = requests.get(NOBLEME_QUOTES_API, {'id': quote_number})

    if response.status_code == 200:
        # remove BOM - blame Bad's code for that
        body = response.text.encode('utf-8').decode('utf-8-sig')
        data = json.loads(body)
        quote = data[0]

        # extract quote's attributes
        is_nsfw = bool(quote.get('quote_nsfw', False))
        texts = quote.get('quote_text', '').splitlines()
        url = quote.get('quote_url', '')
        is_too_long = len(texts) > 2

        # format end message
        template = '[{id}] {url}'
        if is_too_long and not is_nsfw:
            template = '[{id}] Read more at: {url}'

        # send abstract if it's SFW
        if is_nsfw:
            template = template + ' (NSFW)'
        else:
            for text in texts[:2]:
                bot.say(text.strip())

        # send quote's URL
        bot.reply(
            template.format(**{
                'id': quote_number,
                'url': url,
            })
        )
    else:
        bot.reply('Quote "%s" not found.' % quote_number)

    return
