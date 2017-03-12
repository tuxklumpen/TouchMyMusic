from __future__ import unicode_literals

import itertools
import json
import logging
import operator
import urllib.request, urllib.error, urllib.parse
import urllib.parse

#from mopidy import models
#from mopidy.utils import encoding

# NOTE: This module is independent of libspotify and built using the Spotify
# Web APIs. As such it does not tie in with any of the regular code used
# elsewhere in the mopidy-spotify extensions. It is also intended to be used
# across both the 1.x and 2.x versions.

_API_MAX_IDS_PER_REQUEST = 50
_API_BASE_URI = 'https://api.spotify.com/v1/%ss/?ids=%s'

_cache = {}  # (type, id) -> [Image(), ...]

logger = logging.getLogger(__name__)


def get_images(uris):
    result = {}
    uri_type_getter = operator.itemgetter('type')
    uris = sorted((_parse_uri(u) for u in uris), key=uri_type_getter)
    for uri_type, group in itertools.groupby(uris, uri_type_getter):
        batch = []
        for uri in group:
            if uri['key'] in _cache:
                result[uri['uri']] = _cache[uri['key']]
            elif len(batch) < _API_MAX_IDS_PER_REQUEST:
                batch.append(uri)
            else:
                result.update(_process_uris(uri_type, batch))
                batch = []
        result.update(_process_uris(uri_type, batch))
    return result


def _parse_uri(uri):
    parsed_uri = urllib.parse.urlparse(uri)
    uri_type, uri_id = None, None

    if parsed_uri.scheme == 'spotify':
        uri_type, uri_id = parsed_uri.path.split(':')[:2]
    elif parsed_uri.scheme in ('http', 'https'):
        if parsed_uri.netloc in ('open.spotify.com', 'play.spotify.com'):
            uri_type, uri_id = parsed_uri.path.split('/')[1:3]

    if uri_type and uri_type in ('track', 'album', 'artist') and uri_id:
        return {'uri': uri, 'type': uri_type, 'id': uri_id,
                'key': (uri_type, uri_id)}

    raise ValueError('Could not parse %r as a spotify URI' % uri)


def _process_uris(uri_type, uris):
    result = {}
    ids_to_uris = {u['id']: u for u in uris}

    if not uris:
        return result

    try:
        lookup_uri = _API_BASE_URI % (uri_type, ','.join(list(ids_to_uris.keys())))
        data = json.load(urllib.request.urlopen(lookup_uri))
    except (ValueError, IOError) as e:
        error_msg = encoding.locale_decode(e)
        logger.debug('Fetching %s failed: %s', lookup_uri, error_msg)
        return result

    for item in data.get(uri_type + 's', []):
        if not item:
            continue
        uri = ids_to_uris[item['id']]
        if uri['key'] not in _cache:
            if uri_type == 'track':
                album_key = _parse_uri(item['album']['uri'])['key']
                if album_key not in _cache:
                    _cache[album_key] = tuple(
                        _translate_image(i) for i in item['album']['images'])
                _cache[uri['key']] = _cache[album_key]
            else:
                _cache[uri['key']] = tuple(
                    _translate_image(i) for i in item['images'])
        result[uri['uri']] = _cache[uri['key']]

    return result


def _translate_image(i):
    return i
