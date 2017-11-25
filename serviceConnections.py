import rpyc

if __name__ == '__main__':
    from rpyc.utils.server import OneShotServer
    server = OneShotServer(rpyc.SlaveService, port=18888)
    server.start()
