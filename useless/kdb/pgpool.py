import os

class PgPoolConfig(object):
    def __init__(self, cfg, tmpdir):
        object.__init__(self)
        data = {}
        cfg.setGroup('database')
        data['backend_host_name'] = cfg.readEntry('dbhost')
        data['backend_port'] = cfg.readEntry('dbport')
        cfg.setGroup('pgpool')
        data['port'] =cfg.readEntry('port')
        keys = ['num_init_children', 'max_pool',
                'connection_life_time']
        for key in keys:
            data[key] = cfg.readEntry(key)
        while tmpdir[-1] == '/':
            tmpdir = tmpdir[:-1]
        data['logdir'] = "'%s'" % tmpdir
        data['socket_dir'] = "'%s'" % tmpdir
        self.data = data
        self.pidfile = os.path.join(tmpdir, 'pgpool.pid')
        

    def write(self):
        lines = ['%s = %s' % (k,v) for k,v in self.data.items()]
        return '\n'.join(lines) + '\n'

class PgPool(object):
    def __init__(self, cfg, tmpdir, datadir):
        object.__init__(self)
        self.cfg = PgPoolConfig(cfg, tmpdir)
        cfg.setGroup('pgpool')
        self.cmd = cfg.readEntry('command')
        self.conf = os.path.join(datadir, 'pgpool.conf')
        cf = file(self.conf, 'w')
        cf.write(self.cfg.write())
        cf.close()
        self.pidfile = self.cfg.pidfile
        
    def run(self):
        cmd = '%s -f %s' % (self.cmd, self.conf)
        print cmd
        os.system(cmd)

    def stop(self):
        os.system('%s -f %s stop' % (self.cmd, self.conf))
        
        
        
