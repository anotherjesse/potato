#!/usr/bin/env python

import random
import sys
import time

from novaclient.v1_1 import client


def pauseUnpauseSuspendResume(auth_url, tenant, user,
                            password, server_name, timePerAction=20):

    """
        pause, unpause, suspend and resume a
        VM within a specified time for each operation
    """
    nc = client.Client(user, password, tenant, auth_url)

    def get_server(server_name):
        for i in nc.servers.list():
            if i.name == server_name:
                return i
        return False

    def get_random_server():
        servers = [f for f in nc.servers.list()]
        if len(servers):
            return random.choice(servers)
        return False

    if server_name == "random":
        server = get_random_server()
    else:
        server = get_server(server_name)

    assert server, "Instance not found or no available instances"
    print server.name

    def returnServerStatus(server):
        try:
            server.get()
            status = server.status
        except Exception as crapola:
            if crapola == 'This request was rate-limited. (HTTP 413)':
                print "Rate limited: Waiting 5 seconds"
                time.sleep(5)
                return returnServerStatus(server)
        else:
            return status

    def pauseInstance(server):
        try:
            action_start = time.time()
            server.pause()
            actionGood = False
            while (not actionGood and
                        time.time() - action_start < timePerAction):
                if returnServerStatus(server) == 'PAUSED':
                    actionGood = True
                time.sleep(2)
            return actionGood
        except Exception as ex:
            print ex
            return False

    def unpauseInstance(server):
        try:
            action_start = time.time()
            server.unpause()
            actionGood = False
            while (not actionGood and
                        time.time() - action_start < timePerAction):
                if returnServerStatus(server) == 'ACTIVE':
                    actionGood = True
                time.sleep(2)
            return actionGood
        except Exception as ex:
            print ex
            return False

    def suspendInstance(server):
        try:
            action_start = time.time()
            server.suspend()
            actionGood = False
            while (not actionGood and
                        time.time() - action_start < timePerAction):
                if returnServerStatus(server) == 'SUSPENDED':
                    actionGood = True
                time.sleep(2)
            return actionGood
        except Exception as ex:
            print ex
            return False

    def resumeInstance(server):
        try:
            action_start = time.time()
            server.resume()
            actionGood = False
            while (not actionGood and
                        time.time() - action_start < timePerAction):
                if returnServerStatus(server) == 'ACTIVE':
                    actionGood = True
                time.sleep(2)
            return actionGood
        except Exception as ex:
            print ex
            return False

    assert pauseInstance(server), "Instance pause failed"
    assert unpauseInstance(server), "Instance unpause failed"
    assert suspendInstance(server), "Instance suspend failed"
    assert resumeInstance(server), "Instance resume failed"


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

    if len(sys.argv) >= 6:
        server_name = sys.argv[5]
    else:
        server_name = "random"

    pauseUnpauseSuspendResume(auth_url, tenant, user, password, server_name)
    print "success"
