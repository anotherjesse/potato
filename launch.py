#!/usr/bin/env python

import random
import sys
import time
from novaclient.v1_1 import client


def launch(auth_url, tenant, user, password, destroy_time=60):
    """launch and terminate a VM within a specified time"""

    nc = client.Client(user, password, tenant, auth_url)
    name = "test-%d-%d" % (time.time(), random.randint(0, 99999999))

    def get_image(image_name):
        for i in nc.images.list():
            if i.name == image_name:
                return i
        assert None, "Couldn't find image %s" % image_name

    def get_flavor(max_cores):
        flavors = [f for f in nc.flavors.list() if f.vcpus <= max_cores]
        assert len(flavors) > 0, "No flavors"
        return random.choice(flavors)

    image = get_image('oneiric-server-cloudimg-amd64')
    print image

    flavor = get_flavor(4)
    print flavor

    new_server = nc.servers.create(image=image, flavor=flavor, name=name)
    server_id = new_server.id

    print new_server

    while nc.servers.get(server_id).status != 'ACTIVE':
        time.sleep(2)

    nc.servers.delete(server_id)

    start = time.time()
    while time.time() - start < destroy_time:
        if not any([s.id == server_id for s in nc.servers.list()]):
            return
        time.sleep(1)

    assert None, "Server %s wasn't deleted within %d seconds" % (name, destroy_time)


if __name__ == '__main__':
    try:
        import config
    except:
        print "unable to import defaults"

    if len(sys.argv) >= 2:
        tenant = sys.argv[1]
    else:
        tenant = 'admin'

    if len(sys.argv) >= 3:
        user = sys.argv[2]
    else:
        user = tenant

    if len(sys.argv) >= 4:
        password = sys.argv[3]
    else:
        password = config.users[user]

    if len(sys.argv) >= 5:
        auth_url = "http://%s:5000/v2.0/" % sys.argv[4]
    else:
        auth_url = "http://%s:5000/v2.0/" % config.master

    launch(auth_url, tenant, user, password)
    print "success"
