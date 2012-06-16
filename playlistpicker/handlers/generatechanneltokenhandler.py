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

"""Generate a channel token for GAE's channels API.

This is called via an Ajax request.

"""

__author__ = \
  'jeffy@google.com (Jeff Posnick) and jjinux@google.com (JJ Behrens)'

from google.appengine.api import channel

from playlistpicker.handlers.basehandler import BaseHandler
from playlistpicker.utils import channels as channelutils
from playlistpicker.utils import memcache as memcacheutils
from playlistpicker.utils import web as webutils


class GenerateChannelTokenHandler(BaseHandler):
  @BaseHandler.oauth2_decorator.oauth_required
  @BaseHandler.authorize_playlist
  def get(self, playlist_id):
    """Return a channel token."""
    channel_id = channelutils.create_channel_id()
    memcacheutils.update_memcache(channel_id, playlist_id,
                                  self.current_display_name, self.people)
    webutils.render_json_to_response(
      self, dict(channelToken=channel.create_channel(channel_id)))
