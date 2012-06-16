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

"""Let the user create a new playlist."""

__author__ = \
  'jeffy@google.com (Jeff Posnick) and jjinux@google.com (JJ Behrens)'

import uuid

from gdata.service import RequestError
import gdata.youtube
from google.appengine.api import users

from partyjam import model
from partyjam.handlers.basehandler import BaseHandler
from partyjam.utils import web as webutils
from partyjam.utils import youtube as youtubeutils

PLAYLIST_PARAMS = ("name", "description")


class CreatePlaylistHandler(BaseHandler):
  @BaseHandler.oauth2_decorator.oauth_required
  def get(self, template_params=None):
    if template_params is None:
      template_params = {}
    for param in PLAYLIST_PARAMS:
      template_params[param] = self.request.get(param)
    webutils.render_to_response(self, "create_playlist.html", template_params)

  @BaseHandler.oauth2_decorator.oauth_required
  def post(self):
    errors = webutils.require_params(self, PLAYLIST_PARAMS)
    if errors:
      return self.get(dict(errors=errors))
    yt_service = youtubeutils.create_youtube_service(
      self.oauth2_decorator.credentials.access_token)
    try:
      # Make the playlist public so that the other partygoers have access to
      # watch it.
      playlist = yt_service.AddPlaylist(self.request.get("name"),
                                        self.request.get("description"), False)
    except RequestError, e:
      if e.args[0]["status"] != 400:
        raise
      error = "Could not create playlist: %s" % e.args[0]["body"]
      reason = e.args[0]["reason"].strip()
      if reason:
        error += ": %s" % reason
      return self.get(dict(errors=[error]))
    assert isinstance(playlist, gdata.youtube.YouTubePlaylistEntry)
    playlist_metadata = model.PlaylistMetadata(
      owner=users.get_current_user(),
      playlist_id=youtubeutils.get_id_from_uri(playlist),
      uuid=str(uuid.uuid4()))
    playlist_metadata.put()
    edit_url = "%s/playlists/edit/%s" % (
      self.request.host_url, playlist_metadata.playlist_id)
    self.redirect(edit_url)
