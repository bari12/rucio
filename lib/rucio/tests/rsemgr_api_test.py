# Copyright European Organization for Nuclear Research (CERN)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# You may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# http://www.apache.org/licenses/LICENSE-2.0
#
# Authors:
# - Ralph Vigne, <ralph.vigne@cern.ch>, 2012

from rucio.rse import rsemanager


class MgrTestCases():
    files_local = ["1_rse_local_put.raw", "2_rse_local_put.raw", "3_rse_local_put.raw", "4_rse_local_put.raw"]
    files_remote = ['1_rse_remote_get.raw', '2_rse_remote_get.raw', '3_rse_remote_get.raw', '4_rse_remote_get.raw',
                    '1_rse_remote_delete.raw', '2_rse_remote_delete.raw', '3_rse_remote_delete.raw', '4_rse_remote_delete.raw',
                    '1_rse_remote_exists.raw', '2_rse_remote_exists.raw',
                    '1_rse_remote_rename.raw', '2_rse_remote_rename.raw', '3_rse_remote_rename.raw', '4_rse_remote_rename.raw', '5_rse_remote_rename.raw', '6_rse_remote_rename.raw',
                    '7_rse_remote_rename.raw', '8_rse_remote_rename.raw', '9_rse_remote_rename.raw', '10_rse_remote_rename.raw', '11_rse_remote_rename.raw', '12_rse_remote_rename.raw',
                    '1_rse_remote_change_scope.raw',
                    '2_rse_remote_change_scope.raw']

    def __init__(self, tmpdir, rse_tag, user, static_file):
        self.rse_tag = rse_tag
        self.mgr = rsemanager.RSEMgr()
        self.tmpdir = tmpdir
        self.user = user
        self.static_file = static_file

    # Mgr-Tests: GET
    def test_multi_get_mgr_ok(self):
        """(RSE/PROTOCOLS): Get multiple files from storage providing LFNs and PFNs (Success)"""
        pfn_b = self.mgr.lfn2pfn(self.rse_tag, {'name': '4_rse_remote_get.raw', 'scope': 'user.%s' % self.user})
        status, details = self.mgr.download(self.rse_tag, [{'name': '1_rse_remote_get.raw', 'scope': 'user.%s' % self.user},
                                                           {'name': '2_rse_remote_get.raw', 'scope': 'user.%s' % self.user},
                                                           {'name': '3_rse_remote_get.raw', 'scope': 'user.%s' % self.user, 'pfn': self.static_file},
                                                           {'name': '4_rse_remote_get.raw', 'scope': 'user.%s' % self.user, 'pfn': pfn_b}],
                                            self.tmpdir,
                                            protocol_domain='lan', default=True)
        if not (status and details['user.%s:1_rse_remote_get.raw' % self.user] and details['user.%s:2_rse_remote_get.raw' % self.user] and details['user.%s:3_rse_remote_get.raw' % self.user] and details['user.%s:4_rse_remote_get.raw' % self.user]):
            raise Exception('Return not as expected: %s, %s' % (status, details))

    def test_get_mgr_ok_single_lfn(self):
        """(RSE/PROTOCOLS): Get a single file from storage provding the LFN (Success)"""
        self.mgr.download(self.rse_tag, {'name': '1_rse_remote_get.raw', 'scope': 'user.%s' % self.user}, self.tmpdir)

    def test_get_mgr_ok_single_pfn(self):
        """(RSE/PROTOCOLS): Get a single file from storage providing the PFN (Success)"""
        self.mgr.download(self.rse_tag, {'name': '1_rse_remote_get.raw', 'scope': 'user.%s' % self.user, 'pfn': self.static_file}, self.tmpdir)

    def test_get_mgr_SourceNotFound_multi(self):
        """(RSE/PROTOCOLS): Get multiple files from storage providing LFNs  and PFNs (SourceNotFound)"""
        pfn_a = self.mgr.lfn2pfn(self.rse_tag, {'name': '2_rse_remote_get.raw', 'scope': 'user.%s' % self.user})
        pfn_b = self.mgr.lfn2pfn(self.rse_tag, {'name': '2_rse_remote_get_not_existing.raw', 'scope': 'user.%s' % self.user})
        status, details = self.mgr.download(self.rse_tag, [{'name': '1_not_existing_data.raw', 'scope': 'user.%s' % self.user},
                                                           {'name': '1_rse_remote_get.raw', 'scope': 'user.%s' % self.user},
                                                           {'name': '2_not_existing_data.raw', 'scope': 'user.%s' % self.user, 'pfn': pfn_b},
                                                           {'name': '2_rse_remote_get.raw', 'scope': 'user.%s' % self.user, 'pfn': pfn_a}], self.tmpdir)
        if details['user.%s:1_rse_remote_get.raw' % self.user] and details['user.%s:2_rse_remote_get.raw' % self.user]:
            if details['user.%s:1_not_existing_data.raw' % self.user].__class__.__name__ == 'SourceNotFound' and details['user.%s:2_not_existing_data.raw' % self.user].__class__.__name__ == 'SourceNotFound':
                raise details['user.%s:1_not_existing_data.raw' % self.user]
            else:
                raise Exception('Return not as expected: %s, %s' % (status, details))
        else:
            raise Exception('Return not as expected: %s, %s' % (status, details))

    def test_get_mgr_SourceNotFound_single_lfn(self):
        """(RSE/PROTOCOLS): Get a single file from storage providing LFN (SourceNot Found)"""
        self.mgr.download(self.rse_tag, {'name': 'not_existing_data.raw', 'scope': 'user.%s' % self.user}, self.tmpdir)

    def test_get_mgr_SourceNotFound_single_pfn(self):
        """(RSE/PROTOCOLS): Get a single file from storage providing PFN (SourceNotF ound)"""
        pfn = self.mgr.lfn2pfn(self.rse_tag, {'name': 'not_existing_data.raw', 'scope': 'user.%s' % self.user})
        self.mgr.download(self.rse_tag, {'name': 'not_existing_data.raw', 'scope': 'user.%s' % self.user, 'pfn': pfn}, self.tmpdir)

    # Mgr-Tests: PUT
    def test_put_mgr_ok_multi(self):
        """(RSE/PROTOCOLS): Put multiple files to storage (Success)"""
        print 'rse_mgr: bla'
        status, details = self.mgr.upload(self.rse_tag, [{'name': '1_rse_local_put.raw', 'scope': 'user.%s' % self.user}, {'name': '2_rse_local_put.raw', 'scope': 'user.%s' % self.user}], self.tmpdir)
        if not (status and details['user.%s:1_rse_local_put.raw' % self.user] and details['user.%s:2_rse_local_put.raw' % self.user]):
            raise Exception('Return not as expected: %s, %s' % (status, details))

    def test_put_mgr_ok_single(self):
        """(RSE/PROTOCOLS): Put a single file to storage (Success)"""
        self.mgr.upload(self.rse_tag, {'name': '3_rse_local_put.raw', 'scope': 'user.%s' % self.user}, self.tmpdir)

    def test_put_mgr_SourceNotFound_multi(self):
        """(RSE/PROTOCOLS): Put multiple files to storage (SourceNotFound)"""
        status, details = self.mgr.upload(self.rse_tag, [{'name': 'not_existing_data.raw', 'scope': 'user.%s' % self.user}, {'name': '4_rse_local_put.raw', 'scope': 'user.%s' % self.user}], self.tmpdir)
        if details['user.%s:4_rse_local_put.raw' % self.user]:
            raise details['user.%s:not_existing_data.raw' % self.user]
        else:
            raise Exception('Return not as expected: %s, %s' % (status, details))

    def test_put_mgr_SourceNotFound_single(self):
        """(RSE/PROTOCOLS): Put a single file to storage (SourceNotFound)"""
        self.mgr.upload(self.rse_tag, {'name': 'not_existing_data2.raw', 'scope': 'user.%s' % self.user}, self.tmpdir)

    def test_put_mgr_FileReplicaAlreadyExists_multi(self):
        """(RSE/PROTOCOLS): Put multiple files to storage (FileReplicaAlreadyExists)"""
        status, details = self.mgr.upload(self.rse_tag, [{'name': '1_rse_remote_get.raw', 'scope': 'user.%s' % self.user}, {'name': '2_rse_remote_get.raw', 'scope': 'user.%s' % self.user}], self.tmpdir)
        if details['user.%s:1_rse_remote_get.raw' % self.user]:
            raise details['user.%s:2_rse_remote_get.raw' % self.user]
        else:
            raise Exception('Return not as expected: %s, %s' % (status, details))

    def test_put_mgr_FileReplicaAlreadyExists_single(self):
        """(RSE/PROTOCOLS): Put a single file to storage (FileReplicaAlreadyExists)"""
        self.mgr.upload(self.rse_tag, {'name': '1_rse_remote_get.raw', 'scope': 'user.%s' % self.user}, self.tmpdir)

    # MGR-Tests: DELETE
    def test_delete_mgr_ok_multi(self):
        """(RSE/PROTOCOLS): Delete multiple files from storage (Success)"""
        status, details = self.mgr.delete(self.rse_tag, [{'name': '1_rse_remote_delete.raw', 'scope': 'user.%s' % self.user}, {'name': '2_rse_remote_delete.raw', 'scope': 'user.%s' % self.user}])
        if not (status and details['user.%s:1_rse_remote_delete.raw' % self.user] and details['user.%s:2_rse_remote_delete.raw' % self.user]):
            raise Exception('Return not as expected: %s, %s' % (status, details))

    def test_delete_mgr_ok_single(self):
        """(RSE/PROTOCOLS): Delete a single file from storage (Success)"""
        self.mgr.delete(self.rse_tag, {'name': '3_rse_remote_delete.raw', 'scope': 'user.%s' % self.user})

    def test_delete_mgr_SourceNotFound_multi(self):
        """(RSE/PROTOCOLS): Delete multiple files from storage (SourceNotFound)"""
        status, details = self.mgr.delete(self.rse_tag, [{'name': 'not_existing_data.raw', 'scope': 'user.%s' % self.user}, {'name': '4_rse_remote_delete.raw', 'scope': 'user.%s' % self.user}])
        if details['user.%s:4_rse_remote_delete.raw' % self.user]:
            raise details['user.%s:not_existing_data.raw' % self.user]
        else:
            raise Exception('Return not as expected: %s, %s' % (status, details))

    def test_delete_mgr_SourceNotFound_single(self):
        """(RSE/PROTOCOLS): Delete a single file from storage (SourceNotFound)"""
        self.mgr.delete(self.rse_tag, {'name': 'not_existing_data.raw', 'scope': 'user.%s' % self.user})

    # MGR-Tests: EXISTS
    def test_exists_mgr_ok_multi(self):
        """(RSE/PROTOCOLS): Check multiple files on storage (Success)"""
        pfn_a = self.mgr.lfn2pfn(self.rse_tag, {'name': '3_rse_remote_get.raw', 'scope': 'user.%s' % self.user})
        pfn_b = self.mgr.lfn2pfn(self.rse_tag, {'name': '4_rse_remote_get.raw', 'scope': 'user.%s' % self.user})
        status, details = self.mgr.exists(self.rse_tag, [{'name': '1_rse_remote_get.raw', 'scope': 'user.%s' % self.user},
                                                         {'name': '2_rse_remote_get.raw', 'scope': 'user.%s' % self.user},
                                                         {'name': pfn_a},
                                                         {'name': pfn_b}])
        if not (status and details['user.%s:1_rse_remote_get.raw' % self.user] and details['user.%s:2_rse_remote_get.raw' % self.user] and details[pfn_a] and details[pfn_b]):
            raise Exception('Return not as expected: %s, %s' % (status, details))

    def test_exists_mgr_ok_single_lfn(self):
        """(RSE/PROTOCOLS): Check a single file on storage using LFN (Success)"""
        self.mgr.exists(self.rse_tag, {'name': '1_rse_remote_get.raw', 'scope': 'user.%s' % self.user})

    def test_exists_mgr_ok_single_pfn(self):
        """(RSE/PROTOCOLS): Check a single file on storage using PFN (Success)"""
        pfn = self.mgr.lfn2pfn(self.rse_tag, {'name': '1_rse_remote_get.raw', 'scope': 'user.%s' % self.user})
        self.mgr.exists(self.rse_tag, {'name': pfn})

    def test_exists_mgr_false_multi(self):
        """(RSE/PROTOCOLS): Check multiple files on storage (Fail)"""
        pfn_a = self.mgr.lfn2pfn(self.rse_tag, {'name': '2_rse_remote_get.raw', 'scope': 'user.%s' % self.user})
        pfn_b = self.mgr.lfn2pfn(self.rse_tag, {'name': '1_rse_not_existing.raw', 'scope': 'user.%s' % self.user})
        status, details = self.mgr.exists(self.rse_tag, [{'name': '1_rse_remote_get.raw', 'scope': 'user.%s' % self.user},
                                                         {'name': 'not_existing_data.raw', 'scope': 'user.%s' % self.user},
                                                         {'name': pfn_a},
                                                         {'name': pfn_b}])
        if status or not details['user.%s:1_rse_remote_get.raw' % self.user] or details['user.%s:not_existing_data.raw' % self.user] or not details[pfn_a] or details[pfn_b]:
            raise Exception('Return not as expected: %s, %s' % (status, details))

    def test_exists_mgr_false_single_lfn(self):
        """(RSE/PROTOCOLS): Check a single file on storage using LFN (Fail)"""
        not self.mgr.exists(self.rse_tag, {'name': 'not_existing_data.raw', 'scope': 'user.%s' % self.user})

    def test_exists_mgr_false_single_pfn(self):
        """(RSE/PROTOCOLS): Check a single file on storage using PFN (Fail)"""
        pfn = self.mgr.lfn2pfn(self.rse_tag, {'name': '1_rse_not_existing.raw', 'scope': 'user.%s' % self.user})
        not self.mgr.exists(self.rse_tag, {'name': pfn})

    # MGR-Tests: RENAME
    def test_rename_mgr_ok_multi(self):
        """(RSE/PROTOCOLS): Rename multiple files on storage (Success)"""
        pfn_a = self.mgr.lfn2pfn(self.rse_tag, {'name': '7_rse_remote_rename.raw', 'scope': 'user.%s' % self.user})
        pfn_a_new = self.mgr.lfn2pfn(self.rse_tag, {'name': '7_rse_new_rename.raw', 'scope': 'user.%s' % self.user})
        pfn_b = self.mgr.lfn2pfn(self.rse_tag, {'name': '8_rse_remote_rename.raw', 'scope': 'user.%s' % self.user})
        pfn_b_new = self.mgr.lfn2pfn(self.rse_tag, {'name': '8_rse_new_rename.raw', 'scope': 'user.%s' % self.user})
        status, details = self.mgr.rename(self.rse_tag, [{'name': '1_rse_remote_rename.raw', 'scope': 'user.%s' % self.user, 'new_name': '1_rse_remote_renamed.raw'},
                                                         {'name': '2_rse_remote_rename.raw', 'scope': 'user.%s' % self.user, 'new_name': '2_rse_remote_renamed.raw'},
                                                         {'name': pfn_a, 'new_name': pfn_a_new},
                                                         {'name': pfn_b, 'new_name': pfn_b_new}])
        if not status or not (details['user.%s:1_rse_remote_rename.raw' % self.user] and details['user.%s:2_rse_remote_rename.raw' % self.user] and details[pfn_a] and details[pfn_b]):
            raise Exception('Return not as expected: %s, %s' % (status, details))

    def test_rename_mgr_ok_single_lfn(self):
        """(RSE/PROTOCOLS): Rename a single file on storage using LFN (Success)"""
        self.mgr.rename(self.rse_tag, {'name': '3_rse_remote_rename.raw', 'scope': 'user.%s' % self.user, 'new_name': '3_rse_remote_renamed.raw', 'new_scope': 'user.%s' % self.user})

    def test_rename_mgr_ok_single_pfn(self):
        """(RSE/PROTOCOLS): Rename a single file on storage using PFN (Success)"""
        pfn = self.mgr.lfn2pfn(self.rse_tag, {'name': '9_rse_remote_rename.raw', 'scope': 'user.%s' % self.user})
        pfn_new = self.mgr.lfn2pfn(self.rse_tag, {'name': '9_rse_new.raw', 'scope': 'user.%s' % self.user})
        self.mgr.rename(self.rse_tag, {'name': pfn, 'new_name': pfn_new})

    def test_rename_mgr_FileReplicaAlreadyExists_multi(self):
        """(RSE/PROTOCOLS): Rename multiple files on storage (FileReplicaAlreadyExists)"""
        pfn_a = self.mgr.lfn2pfn(self.rse_tag, {'name': '10_rse_remote_rename.raw', 'scope': 'user.%s' % self.user})
        pfn_a_new = self.mgr.lfn2pfn(self.rse_tag, {'name': '1_rse_remote_get.raw', 'scope': 'user.%s' % self.user})
        pfn_b = self.mgr.lfn2pfn(self.rse_tag, {'name': '11_rse_remote_rename.raw', 'scope': 'user.%s' % self.user})
        pfn_b_new = self.mgr.lfn2pfn(self.rse_tag, {'name': '11_rse_new_rename.raw', 'scope': 'user.%s' % self.user})
        status, details = self.mgr.rename(self.rse_tag, [{'name': '4_rse_remote_rename.raw', 'scope': 'user.%s' % self.user, 'new_name': '1_rse_remote_get.raw', 'new_scope': 'user.%s' % self.user},
                                                         {'name': '5_rse_remote_rename.raw', 'scope': 'user.%s' % self.user, 'new_name': '5_rse_new.raw'},
                                                         {'name': pfn_a, 'new_name': pfn_a_new},
                                                         {'name': pfn_b, 'new_name': pfn_b_new}])
        if (not status and details['user.%s:5_rse_remote_rename.raw' % self.user] and details[pfn_b]) and (type(details['user.%s:4_rse_remote_rename.raw' % self.user]) == type(details[pfn_a])):
            raise details['user.%s:4_rse_remote_rename.raw' % self.user]
        else:
            raise Exception('Return not as expected: %s, %s' % (status, details))

    def test_rename_mgr_FileReplicaAlreadyExists_single_lfn(self):
        """(RSE/PROTOCOLS): Rename a single file on storage using LFN (FileReplicaAlreadyExists)"""
        self.mgr.rename(self.rse_tag, {'name': '6_rse_remote_rename.raw', 'scope': 'user.%s' % self.user, 'new_name': '1_rse_remote_get.raw', 'new_scope': 'user.%s' % self.user})

    def test_rename_mgr_FileReplicaAlreadyExists_single_pfn(self):
        """(RSE/PROTOCOLS): Rename a single file on storage using PFN (FileReplicaAlreadyExists)"""
        pfn = self.mgr.lfn2pfn(self.rse_tag, {'name': '12_rse_remote_rename.raw', 'scope': 'user.%s' % self.user})
        pfn_new = self.mgr.lfn2pfn(self.rse_tag, {'name': '1_rse_remote_get.raw', 'scope': 'user.%s' % self.user})
        self.mgr.rename(self.rse_tag, {'name': pfn, 'new_name': pfn_new})

    def test_rename_mgr_SourceNotFound_multi(self):
        """(RSE/PROTOCOLS): Rename multiple files on storage (SourceNotFound)"""
        pfn_a = self.mgr.lfn2pfn(self.rse_tag, {'name': '12_rse_not_existing.raw', 'scope': 'user.%s' % self.user})
        pfn_b = self.mgr.lfn2pfn(self.rse_tag, {'name': '1_rse_not_created.raw', 'scope': 'user.%s' % self.user})
        status, details = self.mgr.rename(self.rse_tag, [{'name': '1_rse_not_existing.raw', 'scope': 'user.%s' % self.user, 'new_name': '1_rse_new_not_created.raw'},
                                                         {'name': pfn_a, 'new_name': pfn_b}])
        if not status and (type(details['user.%s:1_rse_not_existing.raw' % self.user]) == type(details[pfn_a])):
            raise details['user.%s:1_rse_not_existing.raw' % self.user]
        else:
            raise Exception('Return not as expected: %s, %s' % (status, details))

    def test_rename_mgr_SourceNotFound_single_lfn(self):
        """(RSE/PROTOCOLS): Rename a single file on storage using LFN (SourceNotFound)"""
        self.mgr.rename(self.rse_tag, {'name': '1_rse_not_existing.raw', 'scope': 'user.%s' % self.user, 'new_name': '1_rse_new_not_created.raw'})

    def test_rename_mgr_SourceNotFound_single_pfn(self):
        """(RSE/PROTOCOLS): Rename a single file on storage using PFN (SourceNotFound)"""
        pfn = self.mgr.lfn2pfn(self.rse_tag, {'name': '1_rse_not_existing.raw', 'scope': 'user.%s' % self.user})
        pfn_new = self.mgr.lfn2pfn(self.rse_tag, {'name': '1_rse_new_not_created.raw', 'scope': 'user.%s' % self.user})
        self.mgr.rename(self.rse_tag, {'name': pfn, 'new_name': pfn_new})

    def test_change_scope_mgr_ok_single_lfn(self):
        """(RSE/PROTOCOLS): Change the scope of a single file on storage using LFN (Success)"""
        self.mgr.rename(self.rse_tag, {'name': '1_rse_remote_change_scope.raw', 'scope': 'user.%s' % self.user, 'new_scope': 'group.%s' % self.user})

    def test_change_scope_mgr_ok_single_pfn(self):
        """(RSE/PROTOCOLS): Change the scope of a single file on storage using PFN (Success)"""
        pfn = self.mgr.lfn2pfn(self.rse_tag, {'name': '2_rse_remote_change_scope.raw', 'scope': 'user.%s' % self.user})
        pfn_new = self.mgr.lfn2pfn(self.rse_tag, {'name': '2_rse_remote_change_scope.raw', 'scope': 'group.%s' % self.user})
        self.mgr.rename(self.rse_tag, {'name': pfn, 'new_name': pfn_new})
