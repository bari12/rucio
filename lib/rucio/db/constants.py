# Copyright European Organization for Nuclear Research (CERN)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# You may not use this file except in compliance with the License.
# You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0
#
# Authors:
# - Vincent Garonne, <vincent.garonne@cern.ch>, 2013

"""
Constants.

Each constant is in the format:
    CONSTANT_NAME = VALUE, DESCRIPTION
VALUE is what will be stored in the DB.
DESCRIPTION is the meaningful string for client
"""

from datetime import datetime

from rucio.db.enum import DeclEnum


class AccountStatus(DeclEnum):
    ACTIVE = 'ACTIVE', 'ACTIVE'
    SUSPENDED = 'SUSPENDED', 'SUSPENDED'
    DELETED = 'DELETED', 'DELETED'


class AccountType(DeclEnum):
    USER = 'USER', 'USER'
    GROUP = 'GROUP', 'GROUP'
    SERVICE = 'SERVICE', 'SERVICE'


class IdentityType(DeclEnum):
    X509 = 'X509', 'X509'
    GSS = 'GSS', 'GSS'
    USERPASS = 'USERPASS', 'USERPASS'


class ScopeStatus(DeclEnum):
    OPEN = 'O', 'OPEN'
    CLOSED = 'C', 'CLOSED'
    DELETED = 'D', 'DELETED'


class DIDType(DeclEnum):
    FILE = 'F', 'FILE'
    DATASET = 'D', 'DATASET'
    CONTAINER = 'C', 'CONTAINER'
    DELETED_FILE = 'DF', 'DELETED_FILE'
    DELETED_DATASET = 'DD', 'DELETED_DATASET'
    DELETED_CONTAINER = 'DC', 'DELETED_CONTAINER'


class DIDShortType(DeclEnum):
    FILE = 'F', 'FILE'
    DATASET = 'D', 'DATASET'
    CONTAINER = 'C', 'CONTAINER'


class DIDAvailability(DeclEnum):
    LOST = 'L', 'LOST'
    DELETED = 'D', 'DELETED'
    AVAILABLE = 'A', 'AVAILABLE'


class DIDReEvaluation(DeclEnum):
    ATTACH = 'ATTACH', 'ATTACH'
    DETACH = 'DETACH', 'DETACH'
    BOTH = 'BOTH', 'BOTH'


class KeyType(DeclEnum):
    ALL = 'ALL', 'ALL'
    COLLECTION = 'COLLECTION', 'COLLECTION'
    FILE = 'FILE', 'FILE'
    DERIVED = 'DERIVED', 'DERIVED'


class RSEType(DeclEnum):
    DISK = 'DISK', 'DISK'
    TAPE = 'TAPE', 'TAPE'


class ReplicaState(DeclEnum):
    AVAILABLE = 'A', 'AVAILABLE'
    UNAVAILABLE = 'U', 'UNAVAILABLE'
    COPYING = 'C', 'COPYING'
    BEING_DELETED = 'B', 'BEING_DELETED'
    BAD = 'D', 'BAD'


class RuleState(DeclEnum):
    REPLICATING = 'REPLICATING', 'REPLICATING'
    OK = 'OK', 'OK'
    STUCK = 'STUCK', 'STUCK'
    SUSPENDED = 'SUSPENDED', 'SUSPENDED'


class RuleGrouping(DeclEnum):
    ALL = 'A', 'ALL'
    DATASET = 'D', 'DATASET'
    NONE = 'N', 'NONE'


class LockState(DeclEnum):
    REPLICATING = 'R', 'REPLICATING'
    OK = 'O', 'OK'
    STUCK = 'S', 'STUCK'


class SubscriptionState(DeclEnum):
    ACTIVE = 'A', 'ACTIVE'
    INACTIVE = 'I', 'INACTIVE'
    NEW = 'N', 'NEW'
    UPDATED = 'U', 'UPDATED'
    BROKEN = 'B', 'BROKEN'


class RequestType(DeclEnum):
    TRANSFER = 'T', 'TRANSFER'
    DELETE = 'D', 'DELETE'
    UPLOAD = 'U', 'UPLOAD'
    DOWNLOAD = 'D', 'DOWNLOAD'


class RequestState(DeclEnum):
    QUEUED = 'Q', 'QUEUED'
    SUBMITTED = 'S', 'SUBMITTED'
    FAILED = 'F', 'FAILED'
    DONE = 'D', 'DONE'


# Individual constants

OBSOLETE = datetime(year=1970, month=1, day=1)  # Tombstone value to mark obsolete replicas.
