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

"""This module contains stuff related to the datastore."""

__author__ = \
  'jeffy@google.com (Jeff Posnick) and jjinux@google.com (JJ Behrens)'

from google.appengine.ext import db


class PlaylistMetadata(db.Model):
  """This stores the information that we can't put in the YouTube playlist."""
  owner = db.UserProperty()
  playlist_id = db.StringProperty()
  uuid = db.StringProperty()
