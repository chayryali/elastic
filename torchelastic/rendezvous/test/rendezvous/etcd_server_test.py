#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree.

import unittest

from torchelastic.rendezvous.etcd_rendezvous import (
    EtcdRendezvous,
    EtcdRendezvousHandler,
)
from torchelastic.rendezvous.etcd_server import EtcdServer


class EtcdServerTest(unittest.TestCase):
    def test_etcd_server_start_stop(self):
        server = EtcdServer()
        server.start()

        try:
            port = server.get_port()
            host = server.get_host()

            self.assertGreater(port, 0)
            self.assertEqual("localhost", host)
            self.assertEqual(f"{host}:{port}", server.get_endpoint())
            self.assertIsNotNone(server.get_client().version)
        finally:
            server.stop()

    def test_etcd_server_with_rendezvous(self):
        server = EtcdServer()
        server.start()

        rdzv = EtcdRendezvous(
            endpoints=((server.get_host(), server.get_port()),),
            prefix="test",
            run_id=1,
            num_min_workers=1,
            num_max_workers=1,
            timeout=60,
            last_call_timeout=30,
        )
        rdzv_handler = EtcdRendezvousHandler(rdzv)
        store, rank, world_size = rdzv_handler.next_rendezvous()
        self.assertIsNotNone(store)
        self.assertEqual(0, rank)
        self.assertEqual(1, world_size)
