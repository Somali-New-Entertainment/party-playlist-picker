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

"""Serve the XML necessary to create a G+ Hangouts gadget."""

__author__ = \
  'jeffy@google.com (Jeff Posnick) and jjinux@google.com (JJ Behrens)'

from partyjam.handlers.basehandler import BaseHandler
from partyjam.utils import web as webutils


class HangoutsGadgetHandler(BaseHandler):
  def get(self):
    edit_playlist_url = self.request.get("edit_playlist_url", None)
    if edit_playlist_url is None:
      self.error(400)
      self.response.out.write("The edit_playlist_url parameter is required")
      return
    template_params = dict(edit_playlist_url=edit_playlist_url)
    webutils.render_to_response(self, "hangouts_gadget.xml", template_params,
                                content_type="text/xml")