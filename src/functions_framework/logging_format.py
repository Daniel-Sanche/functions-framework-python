# Copyright 2021 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import logging
import os

import flask

class TraceFilter(logging.Filter):
    """
    Logging.Filter subclass class to inject trace data from incoming Flask
    requests into log records. 
    By default, it looks at the X-Cloud-Trace-Context header for trace data.
    If a trace id can't be found, `record.trace` will be an empty string.
    """

    def __init__(self, trace_header='X-Cloud-Trace-Context'):
        self.trace_header = trace_header

    def filter(self, record):
        record.trace = ""
        try:
            if flask and flask.request:
                header = flask.request.headers.get(self.trace_header)
                if header:
                    record.trace = header.split("/", 1)[0]
        except RuntimeError as e:
            # RuntimeError thown when flask session not found
            pass
        return True

class HttpRequestFilter(logging.Filter):
    """
    Logging.Filter subclass class to inject http request data from incoming 
    Flask requests into log records.
    Will insert empty strings when data can't be found.
    """

    def filter(self, record):
        record.request_method = ""
        record.request_url = ""
        record.user_agent = ""
        record.protocol = ""
        try:
            if flask and flask.request:
                record.request_method = flask.request.method
                record.request_url = flask.request.url
                record.user_agent = flask.request.user_agent.string
                record.protocol = flask.request.environ.get("SERVER_PROTOCOL")
        except RuntimeError as e:
            # RuntimeError thown when flask session not found
            pass
        return True

class GcpProjectFilter(logging.Filter):
    """
    Logging.Filter subclass class to inject GCP project data into log records.

    Will insert an empty string when project can't be found.
    """

    def filter(self, record):
        record.gcp_project = os.environ.get("GCP_PROJECT", "")
        return True

def get_format_dict(format_name="plain"):
    """
    Constructs a logging config dictionary to print plain logs
    to standard out
    """
    d = {
        'version': 1,
        'filters': {
            'trace-filter': {
                '()': "functions_framework.logging_format.TraceFilter"
            },
            'http-request-filter': {
                '()': "functions_framework.logging_format.HttpRequestFilter"
            },
            'gcp-project-filter': {
                '()': "functions_framework.logging_format.GcpProjectFilter"
            },
        },
        'formatters':{
            'plain': {
                'format': '%(message)s'
            },
            'structured': {
                'format': '{"message": "%(message)s", "severity": "%(levelname)s"}'
            },
            'gcp': {
                'format': '{"message": "%(message)s", "severity": "%(levelname)s",'
                + ' "logging.googleapis.com/trace": "projects/%(gcp_project)s/traces/%(trace)s",'
                + ' "logging.googleapis.com/sourceLocation": { "file": "%(filename)s", "line": "%(lineno)d",'
                + ' "function": "%(funcName)s"}, "httpRequest": {"requestMethod": "%(request_method)s", '
                + ' "requestUrl": "%(request_url)s", "userAgent": "%(user_agent)s", '
                + ' "protocol": "%(protocol)s"} }'
            }
        },
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
                'formatter': format_name,
                'filters': [
                    "trace-filter",
                    "http-request-filter",
                    "gcp-project-filter"
                ]
            }
        },
        'root': {
            'level': 'DEBUG',
            'handlers': [
                'console'
            ]
        }
    }
    return d

