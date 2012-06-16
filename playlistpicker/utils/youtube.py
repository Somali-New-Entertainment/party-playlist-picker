# Copyright 2011 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""This module has utils related to YouTube."""

__author__ = \
  'jeffy@google.com (Jeff Posnick) and jjinux@google.com (JJ Behrens)'

import re

import atom
import gdata.youtube
from gdata.alt import appengine
from google.appengine.api import app_identity

from playlistpicker.utils import web as webutils

DEVELOPER_KEY = "AI39si4uqTJxCKRpohU_Dl4rejbjQSr3jqFvrk0npzIl4DD3PJDROS9srO12mjIseRnz1Z1cujO-1QurQeAi2DufqAK3mUYdVw"
PLAYLIST_ENTRY_URL_RE = re.compile(
  r"^(http://gdata\.youtube\.com/feeds/api/playlists/[^/]+)/([^/?]+)")
PLAYLIST_URL_PREFIX = "http://gdata.youtube.com/feeds/api/playlists/"


def create_youtube_service(oauth_token=None):
  """Create a YouTubeService object.

  If provided, use the OAuth 2 token. Otherwise, requests are unauthenticated.

  """
  yt_service = gdata.youtube.service.YouTubeService()
  yt_service.ssl = True
  yt_service.client_id = app_identity.get_application_id()
  appengine.run_on_appengine(yt_service, store_tokens=False,
                             single_user_mode=True,
                             deadline=webutils.HTTP_TIMEOUT)
  if oauth_token is not None:
    yt_service.SetAuthSubToken(oauth_token)
  yt_service.developer_key = DEVELOPER_KEY
  return yt_service


def prepare_playlist(entries):
  """Prepare a playlist for the video_list template."""
  rescue = webutils.rescue_default
  ret = []
  for i in entries:
    ret.append(dict(
      id=rescue(lambda: i.id.text),
      title=rescue(lambda: i.title.text),
      description=rescue(lambda: i.description.text),
      duration=rescue(lambda: parse_duration_seconds(i.media.duration.seconds)),
      thumbnail=rescue(lambda: i.media.thumbnail[1].url),
      embeddable=rescue(lambda: is_embeddable(i.media.content), False)))
  return ret


def parse_duration_seconds(seconds):
  """Convert a number of seconds into a human-readable mm:ss string."""
  seconds = int(seconds)
  mm, ss = divmod(seconds, 60)
  return "%d:%02d" % (mm, ss)


def get_id_from_uri(playlist):
  """Given a playlist, return the playlist URI."""
  return playlist.id.text.split('/')[-1]


def write_playlist(handler, yt_service, playlist_id, notify_playlist_listeners):
  """Construct a video_list template and send it via the Channel API.

  The reason you have to pass the notify_playlist_listeners() function is so
  that I can avoid a dependency nightmare.

  """
  (playlist, entries) = fetch_feed_and_entries(
  yt_service.GetYouTubePlaylistVideoFeed, playlist_id=playlist_id)
  template_params = {"video_list": prepare_playlist(entries),
                     "button_name": "Remove", "class_name": "playlist-item",
                     "playlist_id": playlist_id}
  html = webutils.render_to_string("video_list.html", template_params)
  message = dict(action="updateElement", id="playlist", html=html)
  notify_playlist_listeners(playlist_id, message)
  handler.response.out.write("OK")


def fetch_feed_and_entries(get_feed_callback, *args, **kargs):
  """Fetch a feed and all the entries it contains.

  Call get_feed_callback(*args, **kargs) and return a pair (feed, entries_list).
  Take care of paging.

  """
  feed = get_feed_callback(*args, **kargs)
  entries = []
  while feed.entry:
    entries.extend(feed.entry)
    next_link = feed.GetNextLink()
    if next_link is None:
      break
    feed = get_feed_callback(next_link.href)
  return feed, entries


def is_embeddable(media_contents):
  """Determines whether there's an embeddable media content element.

  Returns True if one element in media_contents has yt:format set to 5.
  Returns False otherwise.

  """
  if media_contents:
    for media_content in media_contents:
      if media_content.extension_attributes:
        format = media_content.extension_attributes.get(
          "{http://gdata.youtube.com/schemas/2007}format", "")
        if format == "5":
          return True
  return False


def add_video_to_playlist(yt_service, playlist_url, video_id, position):
  """Adds a video to a playlist, optionally setting the position.

  If position is None, we use the native client library call.
  Otherwise, we construct our own PlaylistVideoEntry and set the position
  attribute, then manually insert it.

  Returns the new gdata.youtube.PlaylistVideoEntry.
  
  """
  if position is None:
    return yt_service.AddPlaylistVideoEntryToPlaylist(playlist_url, video_id)

  playlist_video_entry = gdata.youtube.YouTubePlaylistVideoEntry(
    atom_id=atom.Id(text=video_id),
    position=gdata.youtube.Position(text=position))
  return yt_service.Post(playlist_video_entry, playlist_url,
    converter=gdata.youtube.YouTubePlaylistVideoEntryFromString)