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

"""Let the user rearrange the entries in a playlist."""

__author__ = \
  'jeffy@google.com (Jeff Posnick) and jjinux@google.com (JJ Behrens)'

from playlistpicker.handlers.basehandler import BaseHandler
from playlistpicker.utils import channels as channelutils
from playlistpicker.utils import youtube as youtubeutils


class MovePlaylistEntryHandler(BaseHandler):
  @BaseHandler.oauth2_decorator.oauth_required
  @BaseHandler.authorize_playlist
  @BaseHandler.playlist_entry_uri_required
  def post(self, playlist_id):
    position = int(self.request.get("position"))
    yt_service_for_owner = youtubeutils.create_youtube_service(
      self.owner_oauth_token)
    response = yt_service_for_owner.UpdatePlaylistVideoEntryMetaData(
      self.playlist_uri, self.playlist_entry_id, None, None, position)
    assert response
    youtubeutils.write_playlist(self, yt_service_for_owner, playlist_id,
                                channelutils.notify_playlist_listeners)


