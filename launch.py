#!/usr/bin/env python

import random
import sys
import time
from novaclient.v1_1 import client

def launch(auth_url, tenant='admin', user='admin', password='secrete'):
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

    time.sleep(10)

    for s in nc.servers.list():
        if s.id == server_id:
            assert None, "Server wasn't deleted %s" % server_id


if __name__ == '__main__':
    auth_url = "http://%s:5000/v2.0/" % sys.argv[1]
    tenant = user = password = None
    if len(sys.argv) >= 2:
        tenant = sys.argv[2]
    if len(sys.argv) >= 3:
        user = sys.argv[3]
    if len(sys.argv) >= 4:
        password = sys.argv[4]

    launch(auth_url, tenant, user, password)
    print "success"
