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

"""This gets called when the user disconnects from the channels API."""

__author__ = \
  'jeffy@google.com (Jeff Posnick) and jjinux@google.com (JJ Behrens)'

from playlistpicker.handlers.basehandler import BaseHandler
from playlistpicker.utils import friendlist as friendlistutils
from playlistpicker.utils import memcache as memcacheutils


class DisconnectedHandler(BaseHandler):
  def post(self):
    """Update the list of connected clients and notify the other users."""
    channel_id = self.request.get('from')
    channel = memcacheutils.lookup_channel(channel_id)
    memcacheutils.remove_channel_from_memcache(channel_id)
    friendlistutils.notify_with_new_friend_list(channel["playlist_id"])


