zkdeployment support for docker images
**************************************

This package provides a meta-recipe for deploying and running docker
images.

To use, define a ZooKeeper node of type dockerimage::

  /my
    /application: dockerimage
      version = 0.1.0 # dockerimage version
      image = localhost:5000/fooimage
      ports = "8080:8080 9000-9050:8000-80050 20,21: 3000-30039: 8081"

In this example, we're pulling the docker image from a local
repository.

The ports option defines how container ports are exposed on the host.
The value of the ports option is a string containing one or more
mappings separated by spaces.  A mapping is of one of the following
forms:

  CONTAINTER_PORTS
    The container ports are mapped to ephemeral host ports

  CONTAINTER_PORTS:
    The container ports are mapped to the same ports on the host.

  CONTAINTER_PORTS:HOST_PORTS
    The container ports are mapped to the given host ports. Of course,
    the number of ports must agree.

where CONTAINER_PORTS and HOST_PORTS are lists of ports consisting of
sublists separated by commas. Sublists can be single ports or port
ranges.

You can also use::

  ports = "*"

To map all ports to ephemeral ports and::

  ports = "*:"

to map all exposed ports to the same ports on the server.

Any mapped ports must be exposed by the image.

If no ports option is given, then none of the exposed ports will be
mapped.


If the image defines volumes, some volumes will be automatically
mapped to deployment-specific locations, **if** they're present in the
defined volumes:

  /var/cache
    ${deployment:cache-directory}

  /var/lib
    ${deployment:lib-directory}

  /var/log
    ${deployment:log-directory}

  /var/run
    ${deployment:run-directory}

You can define additional mappings by providing a volumes subnode::

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
          run = None

In this example, the host's ``/mnt/svn`` directory is mapped to the
container's ``/svn`` directory and the host's ``/mnt/ftp`` directory
is mapped to the container's ``/home/ftp`` directory.  The
deployment's log directory is mapped to the container's
``/var/log/myapp`` directory.  The automatic mapping of the
container's ``/var/run`` directory is disabled.

Changes
*******

0.1.0 (yyyy-mm-dd)
==================

Initial release
