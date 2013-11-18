import docker
import json
import hashlib
import zc.metarecipe

standard_volumes = {
    '/var/cache': '${deployment:cache-directory}',
    '/var/lib': '${deployment:lib-directory}',
    '/var/log': '${deployment:log-directory}',
    '/var/run': '${deployment:run-directory}',
    }

class ZKRecipe(zc.metarecipe.Recipe):

    def __init__(self, buildout, name, options):
        super(ZKRecipe, self).__init__(buildout, name, options)

        zk = self.zk = zc.zk.ZK('zookeeper:2181')

        path = '/' + name.rsplit('.', 1)[0].replace(',', '/')
        options = zk.properties(path)

        user = self.user = options.get('user', 'zope')

        self['deployment'] = dict(
            recipe = 'zc.recipe.deployment',
            name=name,
            user=user,
            )

        client = docker.Client()

        image_spec = options['image']
        image_name, tag = image_spec.rsplit(':', 1)

        images = [image for image in client.images(image_name)
                  if image['Tag'] == tag]
        if not images:
            client.pull(image_name, tag=tag)
            images = [image for image in client.images(image_name)
                      if tag is None or image['Tag'] == tag]
            if not images:
                raise ValueError("Couldn't pull", image_spec)

        [image] = images
        image = client.inspect_image(image['Id'])['container_config']

        run_command = ['/usr/bin/docker', 'run']

        ports = options.get('ports', ())
        if ports == '*':
            run_command.append('-P')
        elif ports:
            if ports == '=:*':
                ports = ['%s:%s' % (port, port)
                         for port in sorted(
                             parse_exposed(image['ExposedPorts']))
                         ]
            else:
                ports = parse_ports(
                    ports, set(parse_exposed(image['ExposedPorts'])))

            for port in ports:
                run_command.extend(('-p', port))

        for volume in sorted(image['Volumes']):
            prefix, base = volume.rsplit('/', 1)
            try:
                vpath = zk.resolve(path+'/volumes'+prefix)
            except zc.zk.zookeeper.NoNodeException:
                host_volume = standard_volumes.get(volume)
            else:
                host_volume = zk.properties(vpath).get(base)

            if host_volume:
                run_command.extend(('-v', '%s:%s' % (host_volume, volume)))

        run_command.append(image_spec)
        run_command = ' '.join(run_command)

        self['container'] = dict( # TODO: start-test-program
            recipe = 'zc.zdaemonrecipe',
            deployment = 'deployment',
            program = run_command
            )

        self['rc'] = dict(
            recipe = 'zc.recipe.rhrc',
            deployment = 'deployment',
            parts = 'container',
            chkconfig = '345 99 10',
            digest = hashlib.md5(run_command).hexdigest(),
            **{'process-management': 'true'}
            )

def parse_exposed(exposed):
    for port in exposed:
        if port.endswith('/tcp'):
            yield port[:-4]
        else:
            raise AssertionError('Bad port', port)

def parse_ports(ports, exposed):
    for mapping in ports.strip().split():
        if ':' in mapping:
            to, from_ = mapping.split(':')
            from_ = list(parse_list(from_))
            check_ports(from_, exposed)
            if to == '=':
                to = from_
            else:
                to = list(parse_list(to))
                if not len(from_) == len(to):
                    raise ValueError("different number of from and to ports",
                                     mapping)

            for m in zip(to, from_):
                yield '%s:%s' % m
        else:
            from_ = list(parse_list(mapping))
            check_ports(from_, exposed)
            for port in from_:
                yield str(port)

def parse_list(port_list):
    for port_range in port_list.split(','):
        if '-' in port_range:
            start, end = map(int, port_range.split('-', 1))
            for p in range(start, end+1):
                yield p
        else:
            yield int(port_range)

def check_ports(ports, exposed):
    for port in ports:
        if str(port) not in exposed:
            raise AssertionError("port not exposed", port, exposed)
