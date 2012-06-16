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

"""Let the user edit a playlist."""

__author__ = \
  'jeffy@google.com (Jeff Posnick) and jjinux@google.com (JJ Behrens)'

import re
import simplejson
import urllib

from playlistpicker.handlers.basehandler import BaseHandler
from playlistpicker.utils import friendlist as friendlistutils
from playlistpicker.utils import googleplus as googleplusutils
from playlistpicker.utils import web as webutils
from playlistpicker.utils import youtube as youtubeutils


class EditPlaylistHandler(BaseHandler):
  @BaseHandler.oauth2_decorator.oauth_required
  @BaseHandler.authorize_playlist
  def get(self, playlist_id):
    friend_list = friendlistutils.render_friend_list(playlist_id, self.people)
    template_params = {"button_name": "Remove", "class_name": "playlist-item",
                       "friend_list": friend_list}
    yt_service_for_owner = youtubeutils.create_youtube_service(
      self.owner_oauth_token)
    (playlist, entries) = youtubeutils.fetch_feed_and_entries(
      yt_service_for_owner.GetYouTubePlaylistVideoFeed, playlist_id=playlist_id)

    edit_playlist_url = "%s/playlists/edit/%s?%s" % (
      self.request.host_url, self.playlist_metadata.playlist_id,
      urllib.urlencode({"uuid": self.playlist_metadata.uuid}))
    welcome_page_url = re.sub(r"/edit/", r"/welcome/", edit_playlist_url, 1)
    embedded_edit_playlist_url = edit_playlist_url + "&embedded=1"
    hangouts_gadget_url = "%s/hangouts_gadget.xml?%s" % (
      self.request.host_url,
      urllib.urlencode({"edit_playlist_url": embedded_edit_playlist_url}))
    start_hangout_url = "%s?%s" % (
      googleplusutils.HANGOUTS_URL,
      urllib.urlencode({"gdevurl": hangouts_gadget_url}))

    template_params["title"] = playlist.title.text
    template_params["description"] = playlist.subtitle.text
    template_params["quoted_playlist_id"] = simplejson.dumps(playlist_id)
    template_params["playlist_id"] = playlist_id
    template_params["video_list"] = youtubeutils.prepare_playlist(entries)
    template_params["quoted_edit_url"] = simplejson.dumps(edit_playlist_url)
    template_params["start_hangout_url"] = start_hangout_url
    template_params["quoted_uuid"] = simplejson.dumps(
      self.playlist_metadata.uuid)
    template_params["embedded"] = self.request.get("embedded") == "1"
    template_params["welcome_page_url"] = welcome_page_url
    webutils.render_to_response(self, "edit_playlist.html", template_params)
