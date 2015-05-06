#!/usr/bin/env python
# Copyright European Organization for Nuclear Research (CERN)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# You may not use this file except in compliance with the License.
# You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0
#
# Authors:
# - Mario Lassnig, <mario.lassnig@cern.ch>, 2014-2015
# - Thomas Beermann, <thomas.beermann@cern.ch>, 2014
# - Wen Guan, <wen.guan@cern.ch>, 2014

"""
Hermes is a daemon to deliver messages to an asynchronous broker.
"""

import json
import logging
import os
import random
import socket
import ssl
import sys
import threading
import time
import traceback

import dns.resolver
import stomp

from rucio.common.config import config_get, config_get_int
from rucio.core.heartbeat import live, die, sanity_check
from rucio.core.message import retrieve_messages, delete_messages
from rucio.core.monitor import record_counter
from rucio.db.session import get_session

logging.getLogger("requests").setLevel(logging.CRITICAL)
logging.getLogger("stomp").setLevel(logging.CRITICAL)

logging.basicConfig(stream=sys.stdout,
                    level=getattr(logging, config_get('common', 'loglevel').upper()),
                    format='%(asctime)s\t%(process)d\t%(levelname)s\t%(message)s')

graceful_stop = threading.Event()


class Deliver(object):

    def __init__(self, broker):
        self.__broker = broker
        self.__session = get_session()


def deliver_messages(once=False, brokers_resolved=None, thread=0, bulk=1000):
    """
    Main loop to deliver messages to a broker.
    """

    logging.info('hermes starting - threads (%i) bulk (%i)' % (thread, bulk))
    conns = []
    for broker in brokers_resolved:
        conns.append(stomp.Connection(host_and_ports=[(broker, config_get_int('messaging-hermes', 'port'))],
                                      use_ssl=True,
                                      ssl_key_file=config_get('messaging-hermes', 'ssl_key_file'),
                                      ssl_cert_file=config_get('messaging-hermes', 'ssl_cert_file'),
                                      ssl_version=ssl.PROTOCOL_TLSv1,
                                      reconnect_attempts_max=9999))
    destination = config_get('messaging-hermes', 'destination')

    executable = ' '.join(sys.argv)
    hostname = socket.getfqdn()
    pid = os.getpid()
    hb_thread = threading.current_thread()
    sanity_check(executable=executable, hostname=hostname)

    while not graceful_stop.is_set():

        hb = live(executable, hostname, pid, hb_thread)
        logging.debug('hermes - thread (%i/%i) bulk (%i)' % (hb['assign_thread'],
                                                             hb['nr_threads'],
                                                             bulk))

        try:
            for conn in conns:

                if not conn.is_connected():
                    logging.info('connecting to %s' % conn.transport._Transport__host_and_ports[0][0])
                    record_counter('daemons.hermes.reconnect.%s' % conn.transport._Transport__host_and_ports[0][0].split('.')[0])

                    conn.start()
                    conn.connect()

            tmp = retrieve_messages(bulk=bulk,
                                    thread=hb['assign_thread'],
                                    total_threads=hb['nr_threads'])
            if tmp == []:
                time.sleep(1)
            else:
                to_delete = []
                for t in tmp:
                    try:
                        random.sample(conns, 1)[0].send(body=json.dumps({'event_type': str(t['event_type']).lower(),
                                                                         'payload': t['payload'],
                                                                         'created_at': str(t['created_at'])}),
                                                        destination=destination,
                                                        headers={'persistent': 'true'})
                    except ValueError:
                        logging.warn('Cannot serialize payload to JSON: %s' % str(t['payload']))
                        continue
                    except Exception, e:
                        logging.warn('Could not deliver message: %s' % str(e))
                        continue

                    to_delete.append(t['id'])

                    if str(t['event_type']).lower().startswith("transfer"):
                        logging.debug('%i:%i - event_type: %s, scope: %s, name: %s, rse: %s, request-id: %s, transfer-id: %s, created_at: %s' % (hb['assign_thread'],
                                                                                                                                                 hb['nr_threads'],
                                                                                                                                                 str(t['event_type']).lower(),
                                                                                                                                                 t['payload']['scope'],
                                                                                                                                                 t['payload']['name'],
                                                                                                                                                 t['payload']['dst-rse'],
                                                                                                                                                 t['payload']['request-id'],
                                                                                                                                                 t['payload']['transfer-id'],
                                                                                                                                                 str(t['created_at'])))
                    elif str(t['event_type']).lower().startswith("dataset"):
                        logging.debug('%i:%i - event_type: %s, scope: %s, name: %s, rse: %s, rule-id: %s, created_at: %s)' % (hb['assign_thread'],
                                                                                                                              hb['nr_threads'],
                                                                                                                              str(t['event_type']).lower(),
                                                                                                                              t['payload']['scope'],
                                                                                                                              t['payload']['name'],
                                                                                                                              t['payload']['rse'],
                                                                                                                              t['payload']['rule_id'],
                                                                                                                              str(t['created_at'])))
                    elif str(t['event_type']).lower().startswith("deletion"):
                        if 'url' not in t['payload']:
                            t['payload']['url'] = 'unknown'
                        logging.debug('%i:%i - event_type: %s, scope: %s, name: %s, rse: %s, url: %s, created_at: %s)' % (hb['assign_thread'],
                                                                                                                          hb['nr_threads'],
                                                                                                                          str(t['event_type']).lower(),
                                                                                                                          t['payload']['scope'],
                                                                                                                          t['payload']['name'],
                                                                                                                          t['payload']['rse'],
                                                                                                                          t['payload']['url'],
                                                                                                                          str(t['created_at'])))

                    else:
                        logging.debug('%i:%i -other message: %s' % (hb['assign_thread'], hb['nr_threads'], t))

                delete_messages(to_delete)
        except:
            logging.critical(traceback.format_exc())

    logging.debug('%i:%i - graceful stop requests' % (hb['assign_thread'], hb['nr_threads']))

    for conn in conns:
        try:
            conn.disconnect()
        except:
            pass

    die(executable, hostname, pid, hb_thread)

    logging.debug('%i:%i - graceful stop done' % (hb['assign_thread'], hb['nr_threads']))


def stop(signum=None, frame=None):
    """
    Graceful exit.
    """

    graceful_stop.set()


def run(once=False, threads=1, bulk=1000):
    """
    Starts up the hermes threads.
    """

    if once:
        logging.info('executing one hermes iteration only')
        deliver_messages(once=once, bulk=bulk)

    else:

        logging.info('resolving brokers')

        brokers_alias = []
        brokers_resolved = []
        try:
            brokers_alias = [b.strip() for b in config_get('messaging-hermes', 'brokers').split(',')]
        except:
            raise Exception('Could not load brokers from configuration')

        logging.info('resolving broker dns alias: %s' % brokers_alias)

        brokers_resolved = []
        for broker in brokers_alias:
            brokers_resolved.append([str(tmp_broker) for tmp_broker in dns.resolver.query(broker, 'A')])
        brokers_resolved = [item for sublist in brokers_resolved for item in sublist]

        logging.debug('brokers resolved to %s', brokers_resolved)

        logging.info('starting hermes threads')
        thread_list = [threading.Thread(target=deliver_messages, kwargs={'brokers_resolved': brokers_resolved,
                                                                         'thread': i,
                                                                         'bulk': bulk}) for i in xrange(0, threads)]

        [t.start() for t in thread_list]

        logging.info('waiting for interrupts')

        # Interruptible joins require a timeout.
        while len(thread_list) > 0:
            [t.join(timeout=3.14) for t in thread_list if t and t.isAlive()]
