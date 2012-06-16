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

"""This module has utils for showing a friend list."""

__author__ = \
  'jeffy@google.com (Jeff Posnick) and jjinux@google.com (JJ Behrens)'

from playlistpicker.utils import channels as channelutils
from playlistpicker.utils import memcache as memcacheutils
from playlistpicker.utils import web as webutils


def render_friend_list(playlist_id, people=None):
  """Render a template containing a list of friends.

  If people is None, lookup the list of people from memcache.

  """
  if people is None:
    try:
      people = memcacheutils.lookup_people_given_playlist(playlist_id)
    except KeyError:
      return ""
  memcacheutils.lookup_editing_status(playlist_id, people)
  people.sort(key=lambda p: p["display_name"])
  return webutils.render_to_string("friend_list.html", dict(friends=people))


def notify_with_new_friend_list(playlist_id):
  """Render a new friend list and notify the playlist listeners."""
  html = render_friend_list(playlist_id)
  message = dict(action="updateElement", id="friends", html=html)
  channelutils.notify_playlist_listeners(playlist_id, message)
