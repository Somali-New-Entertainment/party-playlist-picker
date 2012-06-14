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

from google.appengine.api import users

from partyjam.handlers.basehandler import BaseHandler
from partyjam.utils import web as webutils


class WelcomePlaylistHandler(BaseHandler):
  def get(self, playlist_id):
    redirection_url = re.sub(r"/welcome/", r"/edit/", self.request.url, 1)
    quoted_redirection_url = simplejson.dumps(redirection_url)
    template_params = {"quoted_redirection_url": quoted_redirection_url}
    template_params["is_logged_in"] = users.get_current_user() != None
    webutils.render_to_response(self, "welcome_playlist.html", template_params)