# Copyright European Organization for Nuclear Research (CERN)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# You may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# http://www.apache.org/licenses/LICENSE-2.0
#
# Authors:
# - Ralph Vigne, <ralph.vigne@cern.ch>, 2012

import json
import os
import subprocess

from S3.Exceptions import S3Error

from rucio.common import exception
from rucio.rse import wrapper


class TestRseS3():
    def setUp(self):
        """S3 (RSE/PROTOCOLS): Creating necessary directories and files """
        subprocess.call(["mkdir", "/tmp/rucio"], stdout=open(os.devnull, "w"), stderr=subprocess.STDOUT)
        subprocess.call(["mkdir", "/tmp/rucio/local"], stdout=open(os.devnull, "w"), stderr=subprocess.STDOUT)
        subprocess.call(["mkdir", "/tmp/rucio/remote"], stdout=open(os.devnull, "w"), stderr=subprocess.STDOUT)
        subprocess.call(["dd", "if=/dev/urandom", "of=/tmp/rucio/local/1_rse_local.raw", "bs=1024", "count=1024"], stdout=open(os.devnull, "w"), stderr=subprocess.STDOUT)
        subprocess.call(["dd", "if=/dev/urandom", "of=/tmp/rucio/local/2_rse_local.raw", "bs=1024", "count=1024"], stdout=open(os.devnull, "w"), stderr=subprocess.STDOUT)
        # Load local creditentials from file
        credentials = {}
        data = json.load(open('etc/rse-accounts.cfg'))
        credentials = data['swift.cern.ch']
        self.storage = wrapper.RSEWrapper('swift.cern.ch')
        self.storage.connect(credentials)
        # Create test files on storage
        fnull = open(os.devnull, 'w')
        try:
            subprocess.call(["s3cmd", "mb", "s3://RUCIO-TEST"], stdout=fnull, stderr=fnull)
        except S3Error:
            pass
        files = ['1_rse_remote.raw', '2_rse_remote.raw', '3_rse_remote.raw', '4_rse_remote.raw']
        for f in files:
            subprocess.call(["s3cmd", "put", "/tmp/rucio/local/1_rse_local.raw", self.storage.lfn2uri(f), "--no-progress"], stdout=fnull, stderr=fnull)
        fnull.close()

    def tearDown(self):
        """S3 (RSE/PROTOCOLS): Removing created directories and files """
        # Remove test files from storage
        fnull = open(os.devnull, 'w')
        subprocess.call(["s3cmd", "rb", "s3://RUCIO-TEST", "--no-progress", "--force"], stdout=fnull, stderr=fnull)
        fnull.close()
        self.storage.close()
        os.system('rm -rf /tmp/rucio')

    def test_get(self):
        """S3 (RSE/PROTOCOLS): Requesting files from swift.cern.ch """
        gs = True

        # Files are there cases
        # Bulk
        status, details = self.storage.get(['1_rse_remote.raw', '2_rse_remote.raw'], '/tmp/rucio/remote')
        if not status:
            print 'Bulk Mode: Get existing files failed'
            print status, details
            gs = False
        # Single
        try:
            self.storage.get('1_rse_remote.raw', '/tmp/rucio/remote')
        except Exception as e:
            print 'Single Mode: Get existing file failed'
            print e
            gs = False

        # Files do not exists cases
        match = False
        # Bulk
        try:
            status, details = self.storage.get(['not_existing_data.raw', '1_rse_remote.raw'], '/tmp/rucio/remote')
            if details['1_rse_remote.raw']:
                raise details['not_existing_data.raw']
            else:
                gs = False
        except exception.SourceNotFound:
            match = True
        if not match:
            print 'Bulk Mode: Get exsisting and none-existing files failed'
            gs = False
        # Single
        match = False
        try:
            self.storage.get('not_existing_data.raw')
        except exception.SourceNotFound:
            match = True
        if not match:
            print 'Single Mode: Get none-existing file failed'
            gs = False
        assert gs

    def test_put(self):
        """S3 (RSE/PROTOCOLS): Put local file to server """
        gs = True

        # Files are there cases
        # Bulk
        status, details = self.storage.put(['1_rse_local.raw', '2_rse_local.raw'], '/tmp/rucio/local')
        if not status:
            print 'Bulk Mode: Upload existing files failed'
            print status, details
            gs = False
        # Single
        try:
            self.storage.put('1_rse_local.raw', '/tmp/rucio/local')
        except Exception as e:
            print 'Single Mode: Upload existing file failed'
            print e
            gs = False

        # Files do not exists cases
        match = False
        # Bulk
        try:
            status, details = self.storage.put(['not_existing_data.raw', '2_rse_local.raw'], '/tmp/rucio/local')
            if details['2_rse_local.raw']:
                raise details['not_existing_data.raw']
            else:
                gs = False
        except exception.SourceNotFound:
            match = True
        if not match:
            print 'Mix Mode: Upload  with one missing local file failed'
            gs = False
        # Single
        match = False
        try:
            self.storage.put('not_existing_data2.raw', '/tmp/rucio/local')
        except exception.SourceNotFound:
            match = True
        if not match:
            print 'Single Mode: Upload with missing local file falied'
            gs = False
        assert gs

    def test_delete(self):
        """S3 (RSE/PROTOCOLS): Delete file from server """
        gs = True

        # Files are there cases
        # Bulk
        status, details = self.storage.delete(['1_rse_remote.raw', '2_rse_remote.raw'])
        if not status:
            print 'Bulk Mode: Delete existing files failed'
            print status, details
            gs = False
        # Single
        try:
            self.storage.delete('3_rse_remote.raw')
        except Exception as e:
            print 'Single Mode: Delete existing file failed'
            print e
            gs = False

        # Files do not exists cases
        match = False
        # Bulk
        try:
            status, details = self.storage.delete(['not_existing_data.raw', '4_rse_remote.raw'])
            if details['4_rse_remote.raw']:
                raise details['not_existing_data.raw']
            else:
                gs = False
        except exception.SourceNotFound:
            match = True
        if not match:
            print 'Bulk Mode: Delete existing and none-existing files failed'
            gs = False
        # Single
        match = False
        try:
            self.storage.delete('not_existing_data.raw')
        except exception.SourceNotFound:
            match = True
        if not match:
            print 'Single Mode: Delete none-existing file failed'
            gs = False
        assert gs

    def test_exists(self):
        """S3 (RSE/PROTOCOLS): Check if existing files are found and none-existing not """

        gs = True
        status, details = self.storage.exists(['1_rse_remote.raw', '2_rse_remote.raw'])
        if not (details['1_rse_remote.raw'] and details['1_rse_remote.raw']):
            print 'Bulk Mode: Existing files failed'
            gs = False
        status, details = self.storage.exists(['1_rse_remote.raw', 'not_existing_data.raw'])
        if not details['1_rse_remote.raw'] or details['not_existing_data.raw']:
            print 'Bulk Mode: Existing and none-existing files failed'
            gs = False
        if not self.storage.exists('1_rse_remote.raw'):
            print 'Single Mode: Existing file failed'
            gs = False
        if self.storage.exists('not_existing_data.raw'):
            print 'Single Mode: None-existing file failed'
            gs = False
        assert gs

    def test_rename(self):
        """S3 (RSE/PROTOCOLS): Renaming files """
        match = False
        gs = True
        status = None
        details = None
        # Everything fine
        status, details = self.storage.rename({'1_rse_remote.raw': '1_rse_new.raw', '2_rse_remote.raw': '2_rse_new.raw'})
        # Files after renaming: 1_rse_new.raw, 2_rse_new.raw, 3_rse_remote.raw, 4_rse_remote.raw
        if not status or not (details['1_rse_remote.raw'] and details['2_rse_remote.raw']):
            print 'Bulk Mode: Existing files failed'
            gs = False
        try:
            self.storage.rename({'3_rse_remote.raw': '3_rse_new.raw'})
            # Files after renaming: 1_rse_new.raw, 2_rse_new.raw, 3_rse_new.raw, 4_rse_remote.raw
        except Exception as e:
            print 'Single Mode: Existing file failed'
            print e
            gs = False

        # File already exists
        match = False
        status, details = self.storage.rename({'1_rse_new.raw': '2_rse_new.raw', '2_rse_new.raw': '1_rse_new.raw'})
        # Files after renaming: 1_rse_new.raw, 2_rse_new.raw, 3_rse_new.raw, 4_rse_remote.raw
        if status:
            print 'Bulk Mode: All targets exist failed'
            gs = False
        match = False
        try:
            status, details = self.storage.rename({'1_rse_new.raw': '2_rse_new.raw', '4_rse_remote.raw': '4_rse_new.raw'})
            # Files after renaming: 1_rse_new.raw, 2_rse_new.raw, 3_rse_new.raw, 4_rse_new.raw
            if not status:
                if details['4_rse_remote.raw']:
                    raise details['1_rse_new.raw']
        except exception.FileAlreadyExists:
            match = True
        if not match:
            print 'Bulk Mode: Existing and none-existing targets failed'
            print status, details
            gs = False
        match = False
        try:
            self.storage.rename({'3_rse_new.raw': '4_rse_new.raw'})
            # Files after renaming: 1_rse_new.raw, 2_rse_new.raw, 3_rse_new.raw, 4_rse_new.raw
        except exception.FileAlreadyExists:
            match = True
        if not match:
            print 'Single Mode: Existing target failed'
            gs = False

        # Source not found
        match = False
        status, details = self.storage.rename({'1_rse_not_existing.raw': '1_rse_new_not_created.raw', '2_rse_not_existing.raw': '2_rse_new_not_created.raw'})
        # Files after renaming: 1_rse_new.raw, 2_rse_new.raw, 3_rse_new.raw, 4_rse_new.raw
        if status:
            print 'Bulk Mode: Rename none-existing files failed'
            print status, details
            gs = False
        match = False
        try:
            status, details = self.storage.rename({'1_rse_not_existing.raw': '1_rse_new_not_created.raw', '2_rse_new.raw': '2_rse_new_new.raw'})
            # Files after renaming: 1_rse_new.raw, 2_rse_new_new.raw, 3_rse_new.raw, 4_rse_new.raw
            if not status:
                if details['2_rse_new.raw']:
                    raise details['1_rse_not_existing.raw']
        except exception.SourceNotFound:
            match = True
        if not match:
            print 'Bulk Mode: Rename existing and none-existing files failed'
            print status, details
            gs = False
        match = False
        try:
            self.storage.rename({'1_rse_not_existing.raw': '1_rse_new_not_created.raw'})
        except exception.SourceNotFound:
            match = True
        if not match:
            print 'Single Mode: Rename none-existing file failed'
            gs = False
        assert gs
