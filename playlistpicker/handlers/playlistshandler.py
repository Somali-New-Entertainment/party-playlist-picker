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

"""Show the user a list of his playlists."""

__author__ = \
  'jeffy@google.com (Jeff Posnick) and jjinux@google.com (JJ Behrens)'

from google.appengine.api import users

from playlistpicker import model
from playlistpicker.handlers.basehandler import BaseHandler
from playlistpicker.utils import web as webutils
from playlistpicker.utils import youtube as youtubeutils


class PlaylistsHandler(BaseHandler):
  @BaseHandler.oauth2_decorator.oauth_required
  def get(self):
    yt_service = youtubeutils.create_youtube_service(
      self.oauth2_decorator.credentials.access_token)
    (feed, entries) = youtubeutils.fetch_feed_and_entries(
      yt_service.GetYouTubePlaylistFeed, username="default")
    playlists_from_datastore = model.PlaylistMetadata.gql(
      "WHERE owner = :1", users.get_current_user())
    playlist_ids = set(i.playlist_id for i in playlists_from_datastore)
    playlists = []
    for entry in entries:
      id_from_uri = youtubeutils.get_id_from_uri(entry)
      if id_from_uri in playlist_ids:
        playlists.append(dict(id=id_from_uri, title=entry.title.text,
                              num_videos=entry.feed_link[0].count_hint))
    webutils.render_to_response(self, "playlists.html",
                                dict(playlists=playlists))
