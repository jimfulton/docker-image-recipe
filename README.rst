zkdeployment support for docker images
**************************************

This package provides a meta-recipe for deploying and running docker
images.

To use, define a ZooKeeper node of type dockerimage::

  /my
    /application: dockerimage
      version = 0.1.0 # dockerimage version
      image = localhost:5000/fooimage

In this example, we're pulling the docker image from a local
repository.

If the image defines volumes, some volumes will be automatically
mapped to deployment-specific locations:

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
        /mnt
          svn = "/svn"
          ftp = "/home/ftp"

In this example, the host's ``/mnt/svn`` directory is mapped to the
container's ``/svn`` directory and the host's ``/mnt/ftp`` directory
is mapped to the container's ``/home/ftp`` directory.

Changes
*******

0.1.0 (yyyy-mm-dd)
==================

Initial release
