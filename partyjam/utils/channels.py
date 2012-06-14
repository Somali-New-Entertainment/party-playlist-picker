# Copyright 2011 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""This module contains most of the Channel API related code.

We use GAE's Channel API so that users can edit the same playlist in realtime
(i.e. updates from one user automatically show up on another user's screen).

"""

__author__ = \
  'jeffy@google.com (Jeff Posnick) and jjinux@google.com (JJ Behrens)'

import random
import simplejson

from google.appengine.api import channel
from google.appengine.api import users

from partyjam.utils import memcache as memcacheutils


def create_channel_id():
  """Create a channel id based on the current user.
  
  Adds randomness to support the same user using multiple browsers at once.
  
  """
  return "%s:%s" % (users.get_current_user().user_id(),
                    random.random())
  

def notify_playlist_listeners(playlist_id, message):
  """Send message to all connected channels listening for playlist changes.
  
  message will be JSON-encoded before being sent.
  
  """
  channel_ids = memcacheutils.get_channels_for_playlist(playlist_id)
  message = simplejson.dumps(message)
  for channel_id in channel_ids:
    channel.send_message(channel_id, message)
