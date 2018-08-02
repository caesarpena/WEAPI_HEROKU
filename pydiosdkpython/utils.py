# -*- coding: utf-8 -*-
#
#  Copyright 2007-2016 Charles du Jeu - Abstrium SAS <team (at) pyd.io>
#  This file is part of Pydio.
#
#  Pydio is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  Pydio is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with Pydio.  If not, see <http://www.gnu.org/licenses/>.
#
#  The latest code can be found at <http://pyd.io/>.
#

import logging
import requests
import time
import os
import sys
import math
import hashlib

from io import BytesIO, FileIO
from pydispatch import dispatcher
from six import b
from .exceptions import PydioSdkDefaultException

try: # Check wether the SDK in inside PydioSync or Standalone and patch thyself
    from pydio.utils import i18n
    _ = i18n.language.ugettext
except:
    _ = str
try:
    TRANSFER_RATE_SIGNAL
except NameError:
    TRANSFER_RATE_SIGNAL = 'transfer_rate'
    TRANSFER_CALLBACK_SIGNAL = 'transfer_callback'

class BytesIOWithFile(BytesIO):

    def __init__(self, data_buffer, closing_boundary, filename, callback=None, chunk_size=0, file_part=0,
                 signal_sender=None):
        """
        Class extending the standard BytesIO to read data directly from file instead of loading all file content
        in memory. It's initially started with all the necessary data to build the full body of the POST request,
        in an multipart-form-data encoded way.
        It can also feed progress data and transfer rates. When uploading file chunks through various queries, the
        progress takes also into account the fact that this may be the part XX of a larger file.

        :param data_buffer: All the beginning of the multipart data, until the opening of the file content field
        :param closing_boundary: Last data to add after the file content has been sent.
        :param filename: Path of the file on the filesystem
        :param callback: dict() that can be updated with progress data
        :param chunk_size: maximum size that can be posted at once
        :param file_part: if file is bigger that chunk_size, can be 1, 2, 3, etc...
        :return:
        """

        self.callback = callback
        self.cursor = 0
        self.start = time.time()
        self.closing_boundary = closing_boundary
        self.data_buffer_length = len(data_buffer)
        self.file_length = os.stat(filename).st_size
        self.full_length = self.length = self.data_buffer_length + self.file_length + len(closing_boundary)

        self.chunk_size=chunk_size
        self.file_part=file_part
        self._seek = 0
        self._signal_sender=signal_sender

        self.fd = open(filename, 'rb')
        if chunk_size and self.file_length > chunk_size:
            seek = file_part * chunk_size
            self._seek = seek
            self.fd.seek(seek)
            # recompute chunk_size
            if self.file_length - seek < chunk_size:
                self.chunk_size = self.file_length - seek
            self.length = self.chunk_size + self.data_buffer_length + len(closing_boundary)

        BytesIO.__init__(self, data_buffer)

    def __len__(self):
        """
        Override parent method
        :return:int
        """
        return self.length

    def tell(self):
        return self.length

    def read(self, n=-1):
        """
        Override parent method to send the body in correct order
        :param n:int
        :return:data
        """
        #before = time.time()
        if self.cursor >= self.length:
            # EOF
            return
        if self.cursor >= (self.length - len(self.closing_boundary)):
            # CLOSING BOUNDARY
            chunk = self.closing_boundary
        elif self.cursor >= self.data_buffer_length:
            # FILE CONTENT
            if (self.length - len(self.closing_boundary)) - self.cursor <= n:
                n = (self.length - len(self.closing_boundary)) - self.cursor
            chunk = self.fd.read(n)
        else:
            # ENCODED PARAMETERS
            chunk = BytesIO.read(self, n)

        self.cursor += int(len(chunk))

        time_delta = (time.time() - self.start)
        if time_delta > 0:
            transfer_rate = self.cursor//time_delta
        else:
            transfer_rate = sys.maxint

        if self.callback:
            try:
                self.callback(self.full_length, self.cursor + (self.file_part)*self.chunk_size, len(chunk), transfer_rate)
            except Exception as e:
                logging.warning(_('Buffered reader callback error'))
        dispatcher.send(signal=TRANSFER_RATE_SIGNAL, transfer_rate=transfer_rate, sender=self._signal_sender)
        #duration = time.time() - before
        #if duration > 0 :
            #logging.info('Read 8kb of data in %'+str(duration))
        return chunk


def encode_multiparts(fields, basic_auth=None):
    """
    Breaks up the multipart_encoded content into first and last part, to be able to "insert" the file content
    itself in-between
    :param fields: dict() fields to encode
    :return:(header_body, close_body, content_type)
    """
    (data, content_type) = requests.packages.urllib3.filepost.encode_multipart_formdata(fields)
    #logging.debug(data)

    header_body = BytesIO()

    # Remove closing boundary
    lines = data.split("\r\n")
    boundary = lines[0]
    lines = lines[0:len(lines)-2]
    header_body.write(b("\r\n".join(lines) + "\r\n"))

    #Add file data part except data
    header_body.write(b('%s\r\n' % boundary))
    header_body.write(b('Content-Disposition: form-data; name="userfile_0"; filename="fake-name"\r\n'))
    header_body.write(b('Content-Type: application/octet-stream\r\n\r\n'))

    closing_boundary = b('\r\n%s--\r\n' % (boundary))

    return (header_body.getvalue(), closing_boundary, content_type)


def file_start_hash_match(local_file, size, remote_hash):
    md5 = hashlib.md5()
    block_size = 8192
    cursor = 0
    if size < 0:
        logging.error("The size of file cannot be a negative value, seems like 32 bit int value over flow problem, "
                      "check file stat returnned by server")
        return
    with open(local_file,'rb') as f:
        while cursor < size:
            data = f.read(min(block_size, size-cursor))
            if not data:
                break
            cursor += len(data)
            md5.update(data)
    return remote_hash == md5.hexdigest()

