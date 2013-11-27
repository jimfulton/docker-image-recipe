
from zope.testing import setupstack
import gc
import unittest
import manuel.capture
import manuel.doctest
import manuel.testing
import mock
import random
import re
import zc.zk.testing
import zope.testing.renormalizing

def assert_(cond):
    if not cond:
        raise AssertionError

class FauxDockerClient:

    available = {
        ("fooimage", "0.9"): {},
        ("fooimage", "1.0"): dict(
            Id="42",
            container_config=dict(
                PortSpecs = dict(
                    ("%s" % p, {}) for p in
                    ([20, 21, 32, 24, 8080, 8081] +
                     range(9000, 9010) + range(3000,3010))
                    ),
                Volumes = dict((path, {}) for path in ["/var/log", "/var/run"])
                )
            ),
        ("fooimage", "1.0.1"): {},
        ("barimage", "0.1.0"): dict(
            Id="4242",
            container_config=dict(
                PortSpecs = dict(("%s" % p, {}) for p in [8080]),
                Volumes = dict((path, {}) for path in [
                    "/var/log/myapp", "/var/run", "/svn", "/home/ftp"])
                )
            ),
        }

    container = port = _registry_started = None

    def __init__(self):
        self._images = []
        self._byid = {}

    def create_container(self, image, command, environment, detach, ports):
        assert_(image == 'registry')
        assert_(command == '/docker-registry/run.sh')
        assert_(environment == dict(SETTINGS_FLAVOR='prod'))
        assert_(detach)
        assert_(ports == ["5000/tcp"])
        self.container = {}
        return self.container

    def start(self, container):
        assert_(container is self.container)
        self.port = random.randint(9999, 1<<16)
        self.container['NetworkSettings'] = dict(
            PortMapping=dict(Tcp={'5000': self.port}))
        self._registry_started = True

    def stop(self, container):
        assert_(container is self.container)
        assert_(self._registry_started)
        self._registry_started = False

    def remove_container(self, container):
        assert_(container is self.container)
        assert_(not self._registry_started)
        del self.container

    def inspect_container(self, container):
        assert_(container is self.container)
        return container

    def images(self, name):
        return [image for image in self._images if image['Repository'] == name]

    def pull(self, full_name, tag):
        assert_(self._registry_started)
        assert_(full_name.startswith('127.0.0.1:%s/' % self.port))
        name = full_name.split('/')[1]
        image = self.available.get((name, tag))
        if image:
            self._byid[image['Id']] = image
            self._images.append(
                dict(Repository=full_name, Id=image['Id'], Tag=tag))

    def tag(self, id, repository, tag):
        assert_(id in self._byid)
        self._images.append(dict(Repository=repository, Id=id, Tag=tag))

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
