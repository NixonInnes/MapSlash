from random import randint, uniform
from sqlalchemy import and_
from sqlalchemy import Column, Integer, Float, String, ForeignKey, Boolean, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref
from collections import namedtuple, deque

from app import engine, config, session

Base = declarative_base()
Point = namedtuple('Point', ['x', 'y'])

Compass = {
    'nw': Point(-1, 1),
    'n': Point(0, 1),
    'ne': Point(1, 1),
    'w': Point(-1, 0),
    'e': Point(1, 0),
    'sw': Point(-1, -1),
    's': Point(0, -1),
    'se': Point(1, -1)
}



tile_properties = config['tile_properties']

def mean(*args):
    return sum(args) / len(args)


def tile_mixin_factory(tile_properties):
    class TileMixin:
        pass

    for property, default in tile_properties.items():
        setattr(TileMixin, property, Column(Float, default=default))
    return TileMixin


TileMixin = tile_mixin_factory(tile_properties)


class Plane(Base):
    __tablename__ = 'planes'
    id = Column(Integer, primary_key=True)
    name = Column(String)

    origin = relationship('Tile', uselist=False)
    tiles = relationship('Tile', backref='plane')

    @staticmethod
    def create(name='Void', commit=True):
        plane = Plane(name=name)
        plane.create_origin()
        session.add(plane)
        if commit:
            session.commit()
        return plane

    @staticmethod
    def delete(id, commit=True):
        plane = session.query(Plane).get(id)
        if not plane:
            raise Exception(f'No plane with id={id} found!')
        for tile in plane.tiles:
            session.delete(tile)
        session.delete(plane)
        if commit:
            session.commit()


    def create_origin(self, default_properties=config['tile_properties'],
                      commit=True):
        if not self.origin:
            tile = Tile(
                plane=self,
                x=0,
                y=0,
            )

            for property, default in config['tile_properties'].items():
                setattr(tile, property, default)

            session.add(tile)
            self.origin = tile
            self.tiles.append(tile)

        if commit:
            session.commit()

        return self.origin

    @staticmethod
    def generate_uniform(name='Void', max_tiles=1000):
        plane = Plane.create(name=name)

        q = deque()
        q.extend(session.query(Tile).filter(and_(Tile.plane_id==plane.id,
                                                 Tile.edge==True)).all())
        tile_count = len(plane.tiles)
        while tile_count < max_tiles:
            tile = q.popleft()
            new_tiles = generate_around(tile)
            q.extend(new_tiles)
            tile_count += len(new_tiles)
        return plane


    @staticmethod
    def generate_random(name='Void', max_tiles=1000):
        plane = Plane.create(name=name)

        q = deque()
        q.extend(session.query(Tile).filter(and_(Tile.plane_id==plane.id,
                                                 Tile.edge==True)).all())
        tile_count = len(plane.tiles)
        while tile_count < max_tiles:
            q.rotate(randint(-15, 15))
            tile = q.popleft()
            new_tiles = tile.generate_around(tile)
            q.extend(new_tiles)
            tile_count += len(new_tiles)
        return plane


    def __repr__(self):
        return f'<Plane(id={self.id}, name={self.name})>'


class Tile(TileMixin, Base):
    __tablename__ = 'tiles'
    id = Column(Integer, primary_key=True)

    plane_id = Column(Integer, ForeignKey('planes.id'))


    x = Column(Integer, index=True)
    y = Column(Integer, index=True)
    edge = Column(Boolean, default=True, index=True)
    indoors = Column(Boolean, default=False)

    n_id = Column(Integer, ForeignKey('tiles.id'))
    n = relationship('Tile', foreign_keys=[n_id], uselist=False,
                     backref=backref('s', uselist=False, remote_side=[id]))

    ne_id = Column(Integer, ForeignKey('tiles.id'))
    ne = relationship('Tile', foreign_keys=[ne_id], uselist=False,
                      backref=backref('sw', uselist=False, remote_side=[id]))

    e_id = Column(Integer, ForeignKey('tiles.id'))
    e = relationship('Tile', foreign_keys=[e_id], uselist=False,
                     backref=backref('w', uselist=False, remote_side=[id]))

    se_id = Column(Integer, ForeignKey('tiles.id'))
    se = relationship('Tile', foreign_keys=[se_id], uselist=False,
                      backref=backref('nw', uselist=False, remote_side=[id]))

    u_id = Column(Integer, ForeignKey('tiles.id'))
    u = relationship('Tile', foreign_keys=[u_id], uselist=False,
                      backref=backref('d', uselist=False, remote_side=[id]))


    @property
    def coord(self):
        return Point(self.x, self.y)

    @property
    def adjacents(self):
        return {'nw': self.nw,
                'n': self.n,
                'ne': self.ne,
                'e': self.e,
                'se': self.se,
                's': self.s,
                'sw': self.sw,
                'w': self.w}

    def extend(self, direction, commit=True):
        coord_mod = Compass.get(direction)
        if not coord_mod:
            raise Exception("Not a valid compass point.")
        if getattr(self, direction):
            raise Exception('Already a tile in that direction!')
        newtile = Tile(
            plane=self.plane,
            x=self.x + coord_mod.x,
            y=self.y + coord_mod.y,
        )
        query = session.query(Tile).filter(and_(
            Tile.plane_id == self.plane.id,
            Tile.x >= newtile.x - 1,
            Tile.x <= newtile.x + 1,
            Tile.y >= newtile.y - 1,
            Tile.y <= newtile.y + 1
        )).all()

        adjacent_properties = {}
        for prop in config['tile_properties']:
            adjacent_properties[prop] = []


        for qtile in query:
            if qtile is not newtile:
                for prop in adjacent_properties:
                    adjacent_properties[prop].append(getattr(qtile, prop))
                for direction, mod_ in Compass.items():
                    if qtile.x == newtile.x + mod_.x and qtile.y == newtile.y + mod_.y:
                        setattr(newtile, direction, qtile)

        for prop in adjacent_properties:
            setattr(newtile, prop, mean(*adjacent_properties[prop]) * (1+uniform(-0.1, 0.1)))

        self.check_edge()
        newtile.check_edge()

        session.add(newtile)

        if commit:
            session.commit()
        return newtile

    def generate_around(self, commit=True):
        new_tiles = []
        for direction, coord_mod in Compass.items():
            if getattr(self, direction) is None:
                newtile = self.extend(direction, commit=True)
                new_tiles.append(newtile)
        if commit:
            session.commit()
        return new_tiles


    def check_edge(self):
        if all(list(self.adjacents.values())):
            self.edge = False
        else:
            self.edge = True

    def __repr__(self):
        return f'<Tile(id={self.id}, x={self.x}, y={self.y})>'


mob_abilities_table = Table('mob_abilities', Base.metadata,
                            Column('mob_id', Integer, ForeignKey('mobs.id')),
                            Column('ability_id', Integer, ForeignKey('abilities.id')))


class Mob(Base):
    __tablename__ = 'mobs'
    id = Column(Integer, primary_key=True)

    name = Column(String)

    hp = Column(Integer, default=100)
    mn = Column(Integer, default=100)

    str = Column(Integer, default=15)
    int = Column(Integer, default=15)
    wis = Column(Integer, default=15)
    dex = Column(Integer, default=15)
    cha = Column(Integer, default=15)
    lck = Column(Integer, default=15)

    abilities = relationship('Ability', secondary=mob_abilities_table)

    def __repr__(self):
        return f'<Mob(id={self.id}, name={self.name})>'


class Ability(Base):
    __tablename__ = 'abilities'
    id = Column(Integer, primary_key=True)

    name = Column(String)
    targetted = Column(Boolean, default=False)
    cooldown = Column(Integer)
    function = Column(String(48))
    base_damage = Column(Float)




Base.metadata.create_all(engine)
