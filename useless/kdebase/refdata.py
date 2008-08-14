from useless.sqlgen.classes import ColumnType, Column, Table
from useless.sqlgen.statement import Statement
from useless.sqlgen.clause import Eq, In, NotIn

class RefData(object):
    """refcols is a  name, idcol paired dictionary
    refdata[name] is a dictionary of id, record pairs
      where id is from idcol in refcols
    refobject[name] is the object that handles the corresponding refdata
    """
    def __init__(self, refcols):
        object.__init__(self)
        self.cols = refcols
        self.data = {}
        self.object = {}
        for col in refcols:
            self.set_refdata(col, {})
            self.set_refobject(col, None)
            

    def set_refobject(self, column, objeckt):
        self.object[column] = objeckt

    def set_refdata(self, column, refdata):
        self.data[column] = refdata
        
    def copy(self):
        #data and cols remain the same
        newobj = RefData(self.cols)
        newobj.data = self.data
        #object is a new dict that doesn't interfere with this dict
        newobj.object = dict(zip([(k,v) for k,v in self.object.items()]))
        return newobj
    
class DataObject(object):
    def __init__(self):
        object.__init__(self)
        self.stmt = Statement()
        self.id = None
        self.idcol = None
        self.fields = []
        self.table = None
        self.hasMany = {}
        self.hasOne = {}
        
    def select(self, fields=None, table=None, clause=None):
        if fields is None:
            fields = self.fields            
        if table is None:
            table = self.table
        if clause is None:
            clause = Eq(self.idcol, self.id)
        nfields = []
        for field in fields:
            if field in self.hasOne:
                nfields.append(self.hasOne[field].idcol)
            elif field in self.hasMany:
                #nfields.append(self.hasMany[field].idcol)
                pass
            else:
                nfields.append(field)
        #for field in self.hasMany:
            #obj = self.hasMany[field]
            #rtable = self.hasMany_tables[field]
            #clause &= In(obj.idcol, obj.select(fields=[obj.idcol], table=rtable, clause=clause))
        for field in self.hasOne:
            obj = self.hasOne[field]
        return self.stmt.select(fields=nfields, table=table, clause=clause)

    def getMany(self, manyfield, clause=None):
        if clause is None:
            clause = Eq(self.idcol, self.id)
        obj = self.hasMany[manyfield]
        rtable = self.hasMany_tables[manyfield]        
        rid = obj.idcol
        clause = In(obj.idcol, self.stmt.select(fields=[obj.idcol], table=rtable, clause=clause))
        return obj.select(fields=obj.fields, table=obj.table, clause=clause)

    def getAllfields(self, allids=None):
        if allids is None:
            allids = [self.idcol]
        else:
            if self.idcol not in allids:
                allids.append(self.idcol)
        for obj in self.hasMany:
            for field in self.hasMany[obj].getAllfields(allids):
                if field not in allids:
                    allids.append(field)
        for obj in self.hasOne:
            for field in self.hasOne[obj].getAllfields(allids):
                if field not in allids:
                    allids.append(field)
        return allids

    def getData(self, idcol, clause=None):
        ho = [f for f in self.hasOne if self.hasOne[f].idcol == idcol]
        hm = [f for f in self.hasMany if self.hasMany[f].idcol == idcol]
        print ho, hm, 'ho hum'
        if idcol == self.idcol:
            return self.select()
        else:
            if len(hm):
                for f in hm:
                    clause = In(idcol, self.select(fields=[idcol], clause='TRUE'))
                    print clause
        for m, o in self.hasMany.items():
            clause = Eq(self.idcol, self.id)
            rtable = self.hasMany_tables[m]
            sel = self.stmt.select(fields=[o.idcol], table=rtable, clause=clause)
            print In(o.idcol, sel)
            
        
    
class AddressDataObject(DataObject):
    def __init__(self):
        DataObject.__init__(self)
        self.idcol = 'addressid'
        self.fields = ['street1', 'street2', 'city', 'state', 'zip']
        self.table = 'addresses'
        
class ContactDataObject(DataObject):
    def __init__(self):
        DataObject.__init__(self)
        self.idcol = 'contactid'
        self.fields = ['name', 'address', 'email', 'description']
        self.table = 'contacts'
        self.hasMany = dict(address=AddressDataObject())
        self.hasMany_tables = dict(address='contactaddresses')
        

class LocationDataObject(DataObject):
    def __init__(self):
        DataObject.__init__(self)
        self.idcol = 'locationid'
        self.fields = ['name', 'address', 'isp',
                       'connection', 'ip', 'static', 'serviced']
        self.table = 'locations'
        self.hasOne = dict(address=AddressDataObject())
        
    
class ClientDataObject(DataObject):
    def __init__(self):
        DataObject.__init__(self)
        self.idcol = 'clientid'
        self.fields = ['client', 'contacts', 'locations']
        self.table = 'clients'
        self.hasMany = dict(contacts=ContactDataObject(),
                            locations=LocationDataObject())
        self.hasMany_tables = dict(contacts='clientinfo',
                                   locations='clientinfo')

class ObjectMaker(object):
    def __init__(self, type_, idcol=None):
        object.__init__(self)
        if idcol is None:
            idcol = Column('%sid' % type_, ColumnType('int'))
            idcol.constraint.pk = True
        self.idcol = idcol
        self.type = type_
        self.maintable = Table('%ss' % type_, [idcol])
        self._maincols = {}
        self._hasOneTables = {}
        self._hasManyTables = {}
        
    def set_maintablename(self, name):
        self.maintable.name = name

    def append_field(self, name, type='text', width=None):
        coltype = ColumnType(type=type, width=width)
        col = Column(name, coltype)
        self.maintable.columns.append(col)
        self._maincols[name] = col

    def append_manyfield(self, name, type, tablename, reftable):
        coltype = ColumnType(type='int')
        maincol = Column(self.idcol.name, coltype)
        maincol.set_fk(self.maintable.name)
        maincol.constraint.pk = True
        rcol = Column(name, coltype)
        rcol.set_fk(reftable)
        rcol.constraint.pk = True
        self._hasManyTables[type] = Table(tablename, [maincol, rcol])

    def append_manyObject(self, objekt, tablename=None):
        if tablename is None:
            tablename = '%s%s' % (self.type, objekt.type)
        coltype = ColumnType(type='int')
        maincol = Column(self.idcol.name, coltype)
        maincol.set_fk(self.maintable.name)
        rcol = Column(objekt.idcol.name, coltype)
        rcol.set_fk(objekt.maintable.name)
        self._hasManyTables[objekt.type] = Table(tablename, [maincol, rcol])

    def append_oneObject(self, objekt):
        ctype = objekt.idcol.type
        coltype = ColumnType(ctype.type, ctype.width)
        col = Column(objekt.idcol.name, coltype)
        col.set_fk(objekt.maintable.name)
        self.maintable.columns.append(col)
        self._maincols[col.name] = col
        
        
    def _reportme(self):
        print self.maintable
        for table in self._hasManyTables.values():
            print table
            
    
if __name__ == '__main__':
    s = Statement()
    c = ClientDataObject()
    l = LocationDataObject()

    a = AddressDataObject()
    ao = ObjectMaker('address')
    ao.append_field('street1', 'varchar', 200)
    ao.append_field('street2', 'varchar', 200)
    ao.append_field('city', 'varchar', 50)
    ao.append_field('state', 'varchar', 2)
    ao.append_field('zip', 'varchar', 5)
    co = ObjectMaker('contact')
    lo = ObjectMaker('location')
    
    o = ObjectMaker('client')
    #o.set_name('clients')
    o.append_field('name', 'varchar', 45)
    co.append_field('name', 'varchar', 45)
    co.append_oneObject(ao)
    co.append_field('email', 'varchar', 122)
    lo.append_field('name', 'varchar', 45)
    lo.append_oneObject(ao)
    lo.append_field('isp')
    #o.append_manyfield('locationid', 'location', 'clientlocation', 'locations')
    #o.append_manyfield('contactid', 'contact', 'clientcontact', 'contacts')
    o.append_manyObject(co)
    o.append_manyObject(lo)
    
