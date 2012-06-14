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

"""This module contains various initialization routines.

Many of these are HACKs that must be called very early in the application.
That's also why I have to be so careful about the order of imports.

"""

__author__ = \
  'jeffy@google.com (Jeff Posnick) and jjinux@google.com (JJ Behrens)'

import os
import sys


def fix_sys_path():
  """Setup the correct sys.path."""
  third_party = os.path.join(os.path.dirname(__file__), os.pardir, 'third-party')
  if third_party not in sys.path:
    sys.path.insert(0, third_party)


def fix_webapp_util_login_required():

  """Fix webapp_util.login_required.

  HACK: login_required only supports GETs by default.  This breaks the
  OAuth2Decorator when you use it with POST.  Hack it so that it so that
  POSTs just redirect to GET after login.

  """

  import google.appengine.ext.webapp.util as webapp_util
  from google.appengine.api import users

  def login_required(handler_method):

    def check_login(self, *args):
      user = users.get_current_user()
      if not user:
        self.redirect(users.create_login_url(self.request.uri))
      else:
        handler_method(self, *args)

    return check_login

  webapp_util.login_required = login_required


def fix_gdata_authsub_auth_label():
  """HACK: Monkeypatch the client library to support OAuth2."""
  import gdata.auth
  gdata.auth.AUTHSUB_AUTH_LABEL = "OAuth "
