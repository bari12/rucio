# Copyright European Organization for Nuclear Research (CERN)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# You may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# http://www.apache.org/licenses/LICENSE-2.0
#
# Authors:
# - Mario Lassnig, <mario.lassnig@cern.ch>, 2012-2013
# - Thomas Beermann, <thomas.beermann@cern.ch>, 2013
# - Vincent Garonne, <vincent.garonne@cern.ch>, 2013


from datetime import timedelta
from nose.tools import assert_equal, assert_raises, assert_in, raises

from rucio.client.accountclient import AccountClient
from rucio.client.dataidentifierclient import DataIdentifierClient
from rucio.client.metaclient import MetaClient
from rucio.client.rseclient import RSEClient
from rucio.client.scopeclient import ScopeClient
from rucio.common.exception import (DataIdentifierNotFound, UnsupportedOperation,
                                    UnsupportedStatus)
from rucio.common.utils import generate_uuid


class TestIdentifierClients():

    def setup(self):
        self.account_client = AccountClient()
        self.scope_client = ScopeClient()
        self.meta_client = MetaClient()
        self.did_client = DataIdentifierClient()
        self.rse_client = RSEClient()

    def test_add_did(self):
        """ DATA IDENTIFIERS (CLIENT): Add, populate and list did content"""
        tmp_scope = 'scope_%s' % generate_uuid()
        tmp_rse = 'rse_%s' % generate_uuid()
        tmp_dsn = 'dsn_%s' % generate_uuid()

        self.scope_client.add_scope('root', tmp_scope)
        self.rse_client.add_rse(tmp_rse)

        dataset_meta = {'project': 'data13_hip',
                        'run_number': str(generate_uuid()),
                        'stream_name': 'physics_CosmicCalo',
                        'prod_step': 'merge',
                        'datatype': 'NTUP_TRIG',
                        'version': 'f392_m927',
                        }
        sources = []
        for i in xrange(5):
            lfn = '%(tmp_dsn)s.' % locals() + str(generate_uuid())
            pfn = '/castor/cern.ch/grid/atlas/tzero/prod1/perm/%(project)s/%(version)s/%(prod_step)s' % dataset_meta
            pfn += '%(tmp_dsn)s/%(lfn)s' % locals()
            file_meta = {'guid': str(generate_uuid())}
            sources.append({'scope': tmp_scope, 'name': lfn,
                            'size': 724963570L, 'checksum': '0cc737eb',
                            'rse': tmp_rse, 'pfn': pfn, 'meta': file_meta})
        rules = [{'copies': 1, 'rse_expression': 'rse=CERN-PROD_TZERO', 'lifetime': timedelta(days=2)}]
        self.did_client.add_identifier(scope=tmp_scope, name=tmp_dsn, sources=sources, statuses={'monotonic': True}, meta=dataset_meta, rules=rules)

        sources = []
        for i in xrange(5):
            lfn = '%(tmp_dsn)s.' % locals() + str(generate_uuid())
            pfn = '/castor/cern.ch/grid/atlas/tzero/prod1/perm/%(project)s/%(version)s/%(prod_step)s' % dataset_meta
            pfn += '%(tmp_dsn)s/%(lfn)s' % locals()
            file_meta = {'guid': str(generate_uuid())}
            sources.append({'scope': tmp_scope, 'name': lfn,
                            'size': 724963570L, 'checksum': '0cc737eb',
                            'rse': tmp_rse, 'pfn': pfn, 'meta': file_meta})
        rules = [{'copies': 1, 'rse_expression': 'rse=CERN-PROD_TZERO', 'lifetime': timedelta(days=2)}]

        # self.did_client.append_identifier(scope=tmp_scope, name=tmp_dsn, sources=sources)
        self.did_client.set_status(scope=tmp_scope, name=tmp_dsn, open=False)

        # to test nested transaction (for latter)
        #sources = []
        #lfn = '%(tmp_dsn)s.' % locals() + str(generate_uuid())
        #pfn = '/castor/cern.ch/grid/atlas/tzero/prod1/perm/%(project)s/%(version)s/%(prod_step)s' % dataset_meta
        #pfn += '%(tmp_dsn)s/%(lfn)s' % locals()
        #file_meta = {'guid': str(generate_uuid())}
        #sources.append({'scope': tmp_scope, 'name': lfn,
        #                'size': 724963570L, 'checksum': '0cc737eb',
        #                'rse': tmp_rse, 'pfn': pfn, 'meta': file_meta})
        #with assert_raises(DataIdentifierAlreadyExists):
        #    self.did_client.add_identifier(scope=tmp_scope, name=tmp_dsn, sources=sources, statuses={'monotonic': True}, meta=dataset_meta, rules=rules)
        #did = self.did_client.get_did(tmp_scope, lfn)

    def test_exists(self):
        """ DATA IDENTIFIERS (CLIENT): Check if data identifier exists """
        tmp_scope = 'scope_%s' % generate_uuid()
        tmp_file = 'file_%s' % generate_uuid()
        tmp_rse = 'rse_%s' % generate_uuid()

        self.rse_client.add_rse(tmp_rse)
        self.rse_client.add_file_replica(tmp_rse, tmp_scope, tmp_file, 1L, 1L)

        did = self.did_client.get_did(tmp_scope, tmp_file)

        assert_equal(did['scope'], tmp_scope)
        assert_equal(did['name'], tmp_file)

        with assert_raises(DataIdentifierNotFound):
            self.did_client.get_did('i_dont_exist', 'neither_do_i')

    def test_scope_list(self):
        """ DATA IDENTIFIERS (CLIENT): Add, aggregate, and list data identifiers in a scope """

        # create some dummy data
        self.tmp_accounts = ['account_%s' % generate_uuid() for i in xrange(10)]
        self.tmp_scopes = ['scope_%s' % generate_uuid() for i in xrange(10)]
        self.tmp_rses = ['rse_%s' % generate_uuid() for i in xrange(10)]
        self.tmp_files = ['file_%s' % generate_uuid() for i in xrange(10)]
        self.tmp_datasets = ['dataset_%s' % generate_uuid() for i in xrange(10)]
        self.tmp_containers = ['container_%s' % generate_uuid() for i in xrange(10)]

        # add dummy data to the catalogue
        for i in xrange(10):
            self.account_client.add_account(self.tmp_accounts[i], 'user')
            self.scope_client.add_scope(self.tmp_accounts[i], self.tmp_scopes[i])
            self.rse_client.add_rse(self.tmp_rses[i])
            self.rse_client.add_file_replica(self.tmp_rses[i], self.tmp_scopes[i], self.tmp_files[i], 1L, 1L)

        # put files in datasets
        for i in xrange(10):
            for j in xrange(10):
                files = [{'scope': self.tmp_scopes[j], 'name': self.tmp_files[j]}]
                self.did_client.add_identifier(self.tmp_scopes[i], self.tmp_datasets[j], files)

        # put datasets in containers
        for i in xrange(10):
            for j in xrange(10):
                datasets = [{'scope': self.tmp_scopes[j], 'name': self.tmp_datasets[j]}]
                self.did_client.add_identifier(self.tmp_scopes[i], self.tmp_containers[j], datasets)

        # reverse check if everything is in order
        for i in xrange(10):
            result = self.did_client.scope_list(self.tmp_scopes[i])

            r_dids = []
            r_scope = None
            for r in result:
                r_dids.append(r['name'])
                if r_scope is None:
                    r_scope = r['scope']

            assert_in(r_scope, self.tmp_scopes[i])

            for did in result:
                assert_in(self.tmp_files[i], r_dids)
                assert_in(self.tmp_datasets[j], r_dids)
                assert_in(self.tmp_containers[j], r_dids)

    def test_get_did(self):
        """ DATA IDENTIFIERS (CLIENT): add a new data identifier and try to retrieve it back"""

        account = generate_uuid()
        scope = generate_uuid()
        rse = generate_uuid()
        file = generate_uuid()

        self.account_client.add_account(account, 'user')
        self.scope_client.add_scope(account, scope)
        self.rse_client.add_rse(rse)
        self.rse_client.add_file_replica(rse, scope, file, 1L, 1L)

        did = self.did_client.get_did(scope, file)

        assert_equal(did['scope'], scope)
        assert_equal(did['name'], file)

    def test_get_meta(self):
        """ DATA IDENTIFIERS (CLIENT): add a new meta data for an identifier and try to retrieve it back"""

        account = generate_uuid()
        scope = generate_uuid()
        rse = generate_uuid()
        file = generate_uuid()
        keys = []
        values = []
        for i in xrange(10):
            keys.append(generate_uuid())
            values.append(generate_uuid())

        self.account_client.add_account(account, 'user')
        self.scope_client.add_scope(account, scope)
        self.rse_client.add_rse(rse)
        self.rse_client.add_file_replica(rse, scope, file, 1L, 1L)
        for i in xrange(10):
            self.meta_client.add_key(keys[i])
            self.did_client.set_metadata(scope, file, keys[i], values[i])

        meta = self.did_client.get_metadata(scope, file)

        for i in xrange(10):
            assert_equal(meta[keys[i]], values[i])

    def test_list_contents(self):
        """ DATA IDENTIFIERS (CLIENT): test to list contents for an identifier"""

        account = generate_uuid()
        scope = generate_uuid()
        rse = generate_uuid()
        dataset1 = generate_uuid()
        dataset2 = generate_uuid()
        container = generate_uuid()
        files1 = []
        files2 = []
        for i in xrange(10):
            files1.append({'scope': scope, 'name': generate_uuid()})
            files2.append({'scope': scope, 'name': generate_uuid()})

        self.account_client.add_account(account, 'user')
        self.scope_client.add_scope(account, scope)
        self.rse_client.add_rse(rse)
        for i in xrange(10):
            self.rse_client.add_file_replica(rse, scope, files1[i]['name'], 1L, 1L)
            self.rse_client.add_file_replica(rse, scope, files2[i]['name'], 1L, 1L)

        self.did_client.add_identifier(scope, dataset1, files1)
        self.did_client.add_identifier(scope, dataset2, files2)
        datasets = [{'scope': scope, 'name': dataset1}, {'scope': scope, 'name': dataset2}]
        self.did_client.add_identifier(scope, container, datasets)

        contents = self.did_client.list_content(scope, container)

        datasets_s = [d['name'] for d in contents]
        assert_in(dataset1, datasets_s)
        assert_in(dataset2, datasets_s)

    @raises(UnsupportedOperation)
    def test_close(self):
        """ DATA IDENTIFIERS (CLIENT): test to close data identifiers"""

        # Add a scope
        tmp_scope = 'scope_%s' % generate_uuid()
        self.scope_client.add_scope('root', tmp_scope)

        # Add a RSE
        tmp_rse = 'rse_%s' % generate_uuid()
        self.rse_client.add_rse(tmp_rse)

        # Add dataset
        tmp_dataset = 'dsn_%s' % generate_uuid()

        # Add file replica
        tmp_file = 'file_%s' % generate_uuid()
        self.rse_client.add_file_replica(tmp_rse, tmp_scope, tmp_file, 1L, 1L)

        # Add file to dataset
        files = [{'scope': tmp_scope, 'name': tmp_file}, ]
        self.did_client.add_identifier(scope=tmp_scope, name=tmp_dataset, sources=files)

        # Add a second file replica
        tmp_file = 'file_%s' % generate_uuid()
        self.rse_client.add_file_replica(tmp_rse, tmp_scope, tmp_file, 1L, 1L)
        # Add files to dataset
        files = [{'scope': tmp_scope, 'name': tmp_file}, ]
        self.did_client.append_identifier(scope=tmp_scope, name=tmp_dataset, sources=files)

        # Close dataset
        with assert_raises(UnsupportedStatus):
            self.did_client.set_status(scope=tmp_scope, name=tmp_dataset, close=False)
        self.did_client.set_status(scope=tmp_scope, name=tmp_dataset, open=False)

        # Add a third file replica
        tmp_file = 'file_%s' % generate_uuid()
        self.rse_client.add_file_replica(tmp_rse, tmp_scope, tmp_file, 1L, 1L)
        # Add files to dataset
        files = [{'scope': tmp_scope, 'name': tmp_file}, ]
        self.did_client.append_identifier(scope=tmp_scope, name=tmp_dataset, sources=files)
