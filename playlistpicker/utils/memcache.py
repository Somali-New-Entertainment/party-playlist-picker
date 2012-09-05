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

"""This module contains most of the memcache related code.

We mostly use memcache to keep track of which users are editing which
playlists.  This works with the Channel API.

This code is somewhat naive in that it ignores locking and race conditions.

These relationships are stored:

  channels:
    channel_id -> dict(playlist_id=playlist_id,
                       user_id=user_id,
                       display_name=display_name)
  playlist_to_channels:
    playlist_id -> set of channel_ids
  playlist_to_people:
    playlist_id -> list of people

"""

__author__ = \
  'jeffy@google.com (Jeff Posnick) and jjinux@google.com (JJ Behrens)'

from google.appengine.api import memcache

CHANNEL_PLAYLIST_EXPIRATION_SECS = 60 * 60 * 2.5  # 2.5 hours
USER_EXPIRATION_SECS = 60 * 60 * 2  # 2 hours
CIRCLE_EXPIRATION_SECS = 60 * 10  # 10 minutes


def update_memcache(channel_id, playlist_id, user_id, display_name, people):
  """Add a bunch of data to memcache concerning the channels and playlist."""
  assert memcache.set(channel_id,
                      dict(playlist_id=playlist_id, 
                           user_id=user_id,
                           display_name=display_name),
                      namespace="channels",
                      time=CHANNEL_PLAYLIST_EXPIRATION_SECS)
  channel_ids = get_channels_for_playlist(playlist_id)
  channel_ids.add(channel_id)
  assert memcache.set(playlist_id, channel_ids,
                      namespace="playlist_to_channels",
                      time=CHANNEL_PLAYLIST_EXPIRATION_SECS)
  assert memcache.set(playlist_id, people,
                      namespace="playlist_to_people",
                      time=CHANNEL_PLAYLIST_EXPIRATION_SECS)


def remove_channel_from_memcache(channel_id):
  """Remove data for channel_id from memcache."""
  try:
    channel = lookup_channel(channel_id)
  except KeyError:
    return

  playlist_id = channel["playlist_id"]
  memcache.delete(channel_id, namespace="channels")
  channel_ids = get_channels_for_playlist(playlist_id)

  try:
    channel_ids.remove(channel_id)
  except ValueError:
    return
    
  assert memcache.set(playlist_id, channel_ids,
                      namespace="playlist_to_channels",
                      time=CHANNEL_PLAYLIST_EXPIRATION_SECS)
                      

def get_channels_for_playlist(playlist_id):
  """Given a playlist_id, return a set of channel_ids or an empty set if none."""
  return memcache.get(playlist_id, namespace="playlist_to_channels") or set()


def lookup_channel(channel_id):
  """Lookup a channel_id.

  Return what update_memcache stored.
  This may raise a KeyError.

  """
  ret = memcache.get(channel_id, namespace="channels")
  if ret is None:
    raise KeyError(channel_id)
  else:
    return ret


def lookup_people_given_playlist(playlist_id):
  """Lookup a playlist_id.

  Return what update_memcache stored.
  This may raise a KeyError.

  """
  ret = memcache.get(playlist_id, namespace="playlist_to_people")
  if ret is None:
    raise KeyError(playlist_id)
  else:
    return ret


def lookup_editing_status(playlist_id, people):
  """Given a list of people, lookup whether they're editing or not.

  Update the people dicts by adding an "editing" key.

  """
  channel_ids = get_channels_for_playlist(playlist_id)
  channels = memcache.get_multi(channel_ids, namespace="channels")
  editors = set(i["user_id"] for i in channels.values())
  for p in people:
    p["editing"] = p["user_id"] in editors


def cache_call(key, namespace, time, f):
  """Cache the result of a callback."""
  value = memcache.get(key, namespace=namespace)
  if value is None:
    value = f()
    memcache.set(key, value, namespace=namespace, time=time)
  return value