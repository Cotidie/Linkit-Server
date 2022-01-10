from backend.utils import FileType


class BlockQuery():
    def __init__(self, block=None, snode=None, name="", own=False):
        self.block = block
        self.snode = snode
        self.name = name
        self.own = own

    def to_dict(self):
        query = {}
        if self.block:
            query['block'] = self.block
        if self.snode:
            query['snode'] = {'$in': self.snode} if isinstance(self.snode, list) else self.snode
        if self.name:
            query['name'] = self.name
        elif self.own:
            query['name'] = {'$nin': ['.', '..']}

        return query

    def set(self, block: int=None, snode: int=None, name: str=None, own=False):
        self.block = block
        self.snode = snode
        self.name = name
        self.own = own


class SnodeQuery:
    def __init__(self, snode=None, type: FileType=None, owner=None, gid=None, block=None, all=True):
        self.snode = snode
        self.type = type
        self.owner = owner
        self.gid = gid
        self.block = block
        self.all = all

    def to_dict(self):
        query = {}
        if self.snode:
            query['snode'] = self.snode
        if self.type:
            query['type'] = self.type.value
        if self.owner:
            query['owner'] = self.owner
        if self.gid:
            query['gid'] = {'$in': self.gid} if isinstance(self.gid, list) else self.gid
        if self.block:
            query['block'] =  self.block

        return query

    def set(self, snode=None, type: FileType=None, owner=None, group=None, block=None, all=True):
        self.snode = snode
        self.type = type
        self.owner = owner
        self.gid = group
        self.block = block
        self.all = all


class GroupQuery():
    def __init__(self, gid=None, members=None):
        self.gid = gid
        self.members = members

    def to_dict(self):
        query = {}
        if self.gid:
            query['gid'] = self.gid
        if self.members:
            if isinstance(self.members, str):
                query['members'] = self.members
            elif isinstance(self.members, list):
                query['members'] = self.members if len(self.members)>1 else self.members[0]

        return query

    def set(self, gid=None, members=None):
        self.gid = gid
        self.members = members