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

"""This module contains the routing for the application."""

__author__ = \
  'jeffy@google.com (Jeff Posnick) and jjinux@google.com (JJ Behrens)'

from oauth2client.appengine import OAuth2Handler

from partyjam.handlers.addplaylistentryhandler import AddPlaylistEntryHandler
from partyjam.handlers.connectedhandler import ConnectedHandler
from partyjam.handlers.createplaylisthandler import CreatePlaylistHandler
from partyjam.handlers.disconnectedhandler import DisconnectedHandler
from partyjam.handlers.editplaylisthandler import EditPlaylistHandler
from partyjam.handlers.generatechanneltokenhandler import\
  GenerateChannelTokenHandler
from partyjam.handlers.hangoutsgadget import HangoutsGadgetHandler
from partyjam.handlers.moveplaylistentryhandler import MovePlaylistEntryHandler
from partyjam.handlers.playlistshandler import PlaylistsHandler
from partyjam.handlers.removeplaylistentryhandler import\
  RemovePlaylistEntryHandler
from partyjam.handlers.searchhandler import SearchHandler
from partyjam.handlers.welcomehandler import WelcomeHandler
from partyjam.handlers.welcomeplaylisthandler import WelcomePlaylistHandler

ROUTES = [
  ('/', WelcomeHandler),
  ('/playlists', PlaylistsHandler),
  ('/playlists/create', CreatePlaylistHandler),
  ('/playlists/welcome/([^/]+)', WelcomePlaylistHandler),
  ('/playlists/edit/([^/]+)', EditPlaylistHandler),
  ('/playlists/edit/([^/]+)/remove_playlist_entry',
   RemovePlaylistEntryHandler),
  ('/playlists/edit/([^/]+)/move_playlist_entry',
   MovePlaylistEntryHandler),
  ('/playlists/edit/([^/]+)/add_playlist_entry',
   AddPlaylistEntryHandler),
  ('/playlists/edit/([^/]+)/generate_channel_token',
   GenerateChannelTokenHandler),
  ('/search', SearchHandler),
  ('/oauth2callback', OAuth2Handler),
  ('/_ah/channel/connected/', ConnectedHandler),
  ('/_ah/channel/disconnected/', DisconnectedHandler),
  ('/hangouts_gadget.xml', HangoutsGadgetHandler)
]
