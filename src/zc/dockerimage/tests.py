
from zope.testing import setupstack
import gc
import unittest
import manuel.capture
import manuel.doctest
import manuel.testing
import mock
import re
import zc.zk.testing
import zope.testing.renormalizing

class FauxDockerClient:

    available = {
        ("localhost:5000/fooimage", "0.9"): {},
        ("localhost:5000/fooimage", "1.0"): dict(
            Id="42",
            container_config=dict(
                ExposedPorts = dict(
                    ("%s/tcp" % p, {}) for p in
                    ([20, 21, 32, 24, 8080, 8081] +
                     range(9000, 9010) + range(3000,3010))
                    ),
                Volumes = dict((path, {}) for path in ["/var/log", "/var/run"])
                )
            ),
        ("localhost:5000/fooimage", "1.0.1"): {},
        ("localhost:5000/barimage", "0.1.0"): dict(
            Id="4242",
            container_config=dict(
                ExposedPorts = dict(("%s/tcp" % p, {}) for p in [8080]),
                Volumes = dict((path, {}) for path in [
                    "/var/log/myapp", "/var/run", "/svn", "/home/ftp"])
                )
            ),
        }

    def __init__(self):
        self._images = []
        self._byid = {}

    def images(self, name):
        return [image for image in self._images if image['Repository'] == name]

    def pull(self, name, tag):
        image = self.available.get((name, tag))
        if image:
            self._byid[image['Id']] = image
            self._images.append(dict(Repository=name, Id=image['Id'], Tag=tag))

    def inspect_image(self, id):
        return self._byid[id]

def setUp(test):
    zc.zk.testing.setUp(test, '', 'zookeeper:2181')
    client = FauxDockerClient()
    setupstack.context_manager(
        test, mock.patch("docker.Client", side_effect=lambda : client))

def test_suite():
    return unittest.TestSuite((
        manuel.testing.TestSuite(
            manuel.doctest.Manuel() + manuel.capture.Manuel(),
            'main.test',
            setUp=setUp, tearDown=setupstack.tearDown,
            ),
        ))
