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

"""This module contains helpers related to rendering, etc."""

__author__ = \
  'jeffy@google.com (Jeff Posnick) and jjinux@google.com (JJ Behrens)'

import os
import pdb
import simplejson
import sys

from google.appengine.api import users
from google.appengine.ext.webapp import template
import httplib2

HTTP_TIMEOUT = 10


def render_to_string(template_name, template_params=None):
  """Render a template and return it as a string."""
  if template_params is None:
    template_params = {}

  # TODO: Move this logic to a template tag.
  if users.get_current_user():
    template_params["logout_url"] = users.create_logout_url("/")

  path = os.path.join(os.path.dirname(__file__), os.pardir, 'templates',
                      template_name)
  return template.render(path, template_params)


def render_to_response(handler, template_name, template_params=None,
                       content_type=None):
  """Render a template and write it to handler.response.out.

  Optionally, set the "Content-Type" header.

  """
  if content_type is not None:
    handler.response.headers['Content-Type'] = content_type
  handler.response.out.write(
    render_to_string(template_name, template_params))


def render_json_to_response(handler, obj):
  """Serialize obj to JSON and write it out to the response stream."""
  handler.response.headers['Content-Type'] = 'application/json'
  handler.response.out.write(simplejson.dumps(obj))


def rescue_default(callback, default=""):
  """Call callback.  If there's an exception, return default.

  It's convenient to use lambda to wrap the expression in order to
  create a callback.  Only catch IndexError, AttributeError, and ValueError.

  """
  try:
    return callback()
  except (IndexError, AttributeError, ValueError):
    return default


def require_params(handler, params, errors=None):
  if errors is None:
    errors = []
  for param in params:
    if not handler.request.get(param):
      errors.append("Please enter a value for %s." % param)
  return errors


def create_http_with_timeout():
  """Call httplib2.Http and set a time.out."""
  return httplib2.Http(timeout=HTTP_TIMEOUT)


def create_authorized_http_with_timeout(credentials):
  """Call create_http_with_timeout() and set credentials."""
  http = create_http_with_timeout()
  credentials.authorize(http)
  return http
