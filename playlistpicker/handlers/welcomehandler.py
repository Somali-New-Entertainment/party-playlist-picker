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

"""This is the welcome page for the app."""

__author__ = \
  'jeffy@google.com (Jeff Posnick) and jjinux@google.com (JJ Behrens)'

from google.appengine.api import users

from partyjam.handlers.basehandler import BaseHandler
from partyjam.utils import web as webutils


class WelcomeHandler(BaseHandler):
  def get(self):
    if users.get_current_user():
      self.redirect("/playlists")
    else:
      webutils.render_to_response(self, "welcome.html", {})