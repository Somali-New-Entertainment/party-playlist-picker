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

"""This module contains the BaseHandler."""

__author__ = \
  'jeffy@google.com (Jeff Posnick) and jjinux@google.com (JJ Behrens)'

from cgi import escape

from apiclient.errors import HttpError
from gdata.service import RequestError
from google.appengine.api import app_identity, users
from google.appengine.ext import webapp
import httplib2
import logging
from oauth2client.appengine import CredentialsModel, OAuth2Decorator, \
  StorageByKeyName

from playlistpicker import model
from playlistpicker.utils import googleplus as googleplusutils
from playlistpicker.utils import memcache as memcacheutils
from playlistpicker.utils import web as webutils
from playlistpicker.utils import youtube as youtubeutils


class BaseHandler(webapp.RequestHandler):

  """This is the base request handler.

  It contains code that's common to several request handlers.  Some of these
  things couldn't be broken off into the utils directory because they had too
  much knowledge of the request handler's environment.

  """

  # The client_id and client_secret are copied from the API Access tab on
  # the Google APIs Console <http://code.google.com/apis/console>
  oauth2_decorator = OAuth2Decorator(
    client_id='205496663185.apps.googleusercontent.com',
    client_secret='-84bG7a8jGJDRCqD6f8ug_c0',
    scope=" ".join([
      "https://www.googleapis.com/auth/plus.me",
      "http://gdata.youtube.com"
    ]),
    user_agent=app_identity.get_application_id())

  def __init__(self):
    """Set some instance variables.

    I hate to set these here (especially to None!) because they're actually
    set in various decorators.  However, I'm trying to appease PyCharm because
    it's really useful to have it statically figure out where stuff is coming
    from.

    """
    self.current_user_id = None
    self.current_display_name = None
    self.people = None
    self.owner_oauth_token = None
    self.playlist_uri = None
    self.playlist_entry_id = None

  @staticmethod
  def playlist_entry_uri_required(handler_method):

    """This is a decorator to parse the uri parameter.

    Set self.playlist_uri and self.playlist_entry_id.  Automatically handle
    any errors.

    """

    def handle(self, *args, **kargs):
      uri = self.request.get("uri")
      match = youtubeutils.PLAYLIST_ENTRY_URL_RE.match(uri)
      if not match:
        self.error(400)
        self.response.out.write("Invalid uri parameter: %s" % escape(uri))
        return
      self.playlist_uri, self.playlist_entry_id = match.groups()
      return handler_method(self, *args, **kargs)

    return handle

  @staticmethod
  def authorize_playlist(handler_method):
    """Lookup the playlist and check authorization.

    The owner of the playlist can always edit the playlist.  Other users can
    only edit the playlist if they have the right uuid in the URL.

    This decorator wraps handler methods.  The handler method must receive a
    playlist_id argument, and it must use @decorator.oauth_required before
    this decorator.

    This decorator will set:

      - self.playlist_metadata
      - self.people
      - self.current_user_id
      - self.current_display_name
      - self.owner_oauth_token

    """

    def handle(self, playlist_id):
      try:
        self.playlist_metadata = model.PlaylistMetadata.gql(
          "WHERE playlist_id = :1", playlist_id)[0]
      except IndexError:
        self.error(404)
        self.response.out.write("Party Playlist Picker does not know about playlist %s." %
                                escape(playlist_id))
        return

      if users.get_current_user() != self.playlist_metadata.owner:
        if self.request.get("uuid", -1) != self.playlist_metadata.uuid:
          self.error(401)
          self.response.out.write("You are not authorized to view this page.")
          return

      owner_id = self.playlist_metadata.owner.user_id()
      owner_credentials = StorageByKeyName(CredentialsModel, owner_id,
                                           'credentials').get()
      self.owner_oauth_token = owner_credentials.access_token

      me = memcacheutils.cache_call(
        key=self.oauth2_decorator.credentials.access_token,
        namespace="oauth2_token_to_user",
        time=memcacheutils.USER_EXPIRATION_SECS,
        f=lambda: googleplusutils.service.people().get(userId="me").execute(
          webutils.create_authorized_http_with_timeout(
            self.oauth2_decorator.credentials)))
      self.current_user_id = me["id"]
      self.current_display_name = me["displayName"]

      # TODO: Front some of the following datastore lookups with memcache.
      query = model.Person.all().filter("user_id = ", me["id"])
      person = query.get()
      if person is None:
        person = model.Person(
          user_id=me["id"],
          display_name=me["displayName"],
          image_url=me.get("image", {}).get("url",
            "/static/images/default_profile.jpg"),
          profile_url=me["url"]
        )
        person.put()

      query = model.PlaylistEditors.all().filter("playlist_id = ",
        playlist_id).ancestor(person)
      if query.get() is None:
        model.PlaylistEditors(parent=person, playlist_id=playlist_id).put()

      # We'll probably end up moving this out of the decorator entirely.
      self.people = []
      playlist_editors = model.PlaylistEditors.all().filter("playlist_id = ",
        playlist_id)
      for playlist_editor in playlist_editors:
        person = playlist_editor.parent()
        self.people.append(dict(
          user_id=person.user_id,
          display_name=person.display_name,
          image_url=person.image_url,
          profile_url=person.profile_url
        ))

      handler_method(self, playlist_id)

    return handle

  def handle_exception(self, exception, debug_mode):
    """Handle certain global exceptions such as OAuth2 problems."""
    if (isinstance(exception, RequestError) and
        exception.args[0]["status"] == 401):
      body = exception.args[0]["body"]
      if "Stateless token expired" in body:
        self._force_refresh()
        self.redirect(self.request.url)
        return
      if "NoLinkedYouTubeAccount" in body:
        webutils.render_to_response(self, "unlinked_account.html")
        return
    webapp.RequestHandler.handle_exception(self, exception, debug_mode)

  @oauth2_decorator.oauth_required
  def _force_refresh(self):
    """HACK: Force the refresh of the OAuth2 token."""
    self.oauth2_decorator.credentials._refresh(httplib2.Http().request)

  def redirect(self, uri, permanent=False):
    """HACK: Fix OAuth problems that occur when embedded.

    The OAuth2Decorator works by redirecting the user to an OAuth page if
    we need certain permissions.  That doesn't work if the application is
    running inside an iframe (e.g. when we're embedded in a hangout).  Catch
    the attempted redirect, and handle the situation in a more manual way.

    """
    if (uri.startswith("https://accounts.google.com/o/oauth2/auth") and
        self.request.get("embedded") == "1"):
      logging.info(
        "Hijacking the OAuth flow because it won't work in an iframe")
      template_params = dict(oauth_uri=uri, continuation_uri=self.request.url)
      webutils.render_to_response(self, "embedded_oauth.html",
        template_params)
    else:
      webapp.RequestHandler.redirect(self, uri, permanent)
