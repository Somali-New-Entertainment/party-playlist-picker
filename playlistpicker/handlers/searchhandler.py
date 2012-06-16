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

"""Let the user search for videos."""

__author__ = \
  'jeffy@google.com (Jeff Posnick) and jjinux@google.com (JJ Behrens)'

import gdata.youtube.service

from playlistpicker.handlers.basehandler import BaseHandler
from playlistpicker.utils import web as webutils
from playlistpicker.utils import youtube as youtubeutils


class SearchHandler(BaseHandler):
  def get(self):
    """Return an HTML fragment of YT search results."""
    q = self.request.get("q")
    yt_service = youtubeutils.create_youtube_service()
    query = gdata.youtube.service.YouTubeVideoQuery()
    query.vq = q
    results_feed = yt_service.YouTubeQuery(query)
    video_list = [
      dict(id=youtubeutils.get_id_from_uri(i),
           title=i.media.title.text,
           description=i.media.description.text,
           duration=youtubeutils.parse_duration_seconds(
             i.media.duration.seconds),
           thumbnail=i.media.thumbnail[1].url,
           embeddable=youtubeutils.is_embeddable(i.media.content))
      for i in results_feed.entry
    ]
    template_params = {"button_name": "Add", "class_name": "search-item",
                       "video_list": video_list}
    webutils.render_to_response(self, "video_list.html", template_params)