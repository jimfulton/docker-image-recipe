zkdeployment support for docker images
**************************************

This package provides a meta-recipe for deploying and running docker
images.

To use, define a ZooKeeper node of type dockerimage::

  /my
    /application: dockerimage
      version = 0.1.0 # dockerimage version
      image = localhost:5000/fooimage
      ports = "8080:8080 8000-80050:9000-9050 =:20,21 =:3000-30039 8081"

In this example, we're pulling the docker image from a local
repository.

The ports option defines how container ports are exposed on the host.
The value of the ports option is a string containing one or more
mappings separated by spaces.  A mapping is of one of the following
forms:

  CONTAINTER_PORTS
    The container ports are mapped to ephemeral host ports

  =:CONTAINTER_PORTS
    The container ports are mapped to the same ports on the host.

  HOST_PORTS:CONTAINTER_PORTS
    The container ports are mapped to the given host ports. Of course,
    the number of ports must agree.

where CONTAINER_PORTS and HOST_PORTS are lists of ports consisting of
sublists separated by commas. Sublists can be single ports or port
ranges.

You can also use::

  ports = "*"

To map all ports to ephemeral ports and::

  ports = "=:*"

to map all exposed ports to the same ports on the server.

Any mapped ports must be exposed by the image.

If no ports option is given, then none of the exposed ports will be
mapped.

Note that host ports are exposed on all interfaces. In the future,
support for sepcifying interfaces will likely be added.

You can define volume mappings by providing a volumes subnode::

  /my
    /application: dockerimage
      version = 0.1.0 # dockerimage version
      image = localhost:5000/fooimage
      /volumes
        svn = "/mnt/svn"
        /home
          ftp = "/mnt/ftp"
        /var
          /log
            myapp = "${deployment:log-directory}

In this example, the host's ``/mnt/svn`` directory is mapped to the
container's ``/svn`` directory and the host's ``/mnt/ftp`` directory
is mapped to the container's ``/home/ftp`` directory.  The
deployment's log directory is mapped to the container's
``/var/log/myapp`` directory.

Changes
*******

0.3.0 (2014-01-20)
==================

When starting containers, pass lxc configuration to set a host name
for a container based on the host's host name and the ZooKeeper path.

0.2.8 (2013-11-30)
==================

Fixed: incorrect docker path

0.2.7 (2013-11-30)
==================

Fixed: typoed cleanpython27 dependency

0.2.6 (2013-11-30)
==================

Fixed: missing dependency on the registry rpm.

0.2.5 (2013-11-29)
==================

Fixed: Missing dependency, zdaemon

Fixed: Failed to work with zkdeploy because test for getting options
       from ZooKeeper was incorrect.

Fixed: Unicode was leaking through to buildout.

0.2.4 (2013-11-27)
==================

Fixed: recipe dependencies

0.2.3 (2013-11-27)
==================

Fixed: packaging

0.2.2 (2013-11-27)
==================

Fixed: packaging

0.2.1 (2013-11-27)
==================

Fixed: zookeeper-deploy script

0.2.0 (2013-11-27)
==================

- Added environment variable support.

- Made volume mapping purely explicit.

- Start and stop a local registry when pulling.

- Fixed: missing recipe entry point

- Fixed: generated program lines lacked -rm options to remove
  containers after running images.

- Fixed: didn't work with docker 0.6.4 because of meta-data
  differences.

- Fixed: didn't run as root by default

0.1.0 (2013-11-20)
==================

Initial release
