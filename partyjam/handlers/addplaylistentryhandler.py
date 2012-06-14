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

"""Let the user add a playlist entry."""

__author__ = \
  'jeffy@google.com (Jeff Posnick) and jjinux@google.com (JJ Behrens)'

from partyjam.handlers.basehandler import BaseHandler
from partyjam.utils import channels as channelutils
from partyjam.utils import youtube as youtubeutils


class AddPlaylistEntryHandler(BaseHandler):
  @BaseHandler.oauth2_decorator.oauth_required
  @BaseHandler.authorize_playlist
  def post(self, playlist_id):
    video_id = self.request.get("video_id")
    position = self.request.get("position", None)
    playlist_url = youtubeutils.PLAYLIST_URL_PREFIX + playlist_id
    yt_service_for_owner = youtubeutils.create_youtube_service(
      self.owner_oauth_token)
    response = youtubeutils.add_video_to_playlist(yt_service_for_owner,
                                                  playlist_url, video_id,
                                                  position)
    assert response
    youtubeutils.write_playlist(self, yt_service_for_owner, playlist_id,
                                channelutils.notify_playlist_listeners)


