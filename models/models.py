from sqlalchemy import String, Column, Integer, Date
from sqlalchemy.ext.declarative import declarative_base

Model = declarative_base(name='Model')


class Resources(Model):
    __tablename__ = 'resources'

    id = Column('id', Integer, primary_key=True)
    type = Column('type', Integer)
    city_id = Column('city_id', Integer)
    name = Column('name', String(255))
    url = Column('url', String)
    owner_id = Column('owner_id', String)
    date = Column('date', Date)
    s_date = Column('s_date', Date)
    f_date = Column('f_date', Date)
    met_finish_date = Column('met_finish_date', Date)
    description = Column('description', String)
    photo = Column('photo', String)
    place = Column('place', String(255))
    status = Column('status', Integer)

    def __repr__(self) -> str:
        return f'Resource(id={self.id!r}, ' \
               f'type={self.type!r}, ' \
               f'name={self.name!r}, ' \
               f'\ndescription={self.description!r})'


class ResourceMetrics(Model):
    __tablename__ = 'sub_follow'

    id = Column('id', Integer, primary_key=True)
    type = Column('type', Integer)
    res_id = Column('res_id', Integer)
    sf_type = Column('sf_type', String(255))
    count = Column('count', Integer)
    date = Column('date', Date)


class Posts(Model):
    __tablename__ = 'res_posts'

    id = Column('id', Integer, primary_key=True)
    type = Column('type', Integer)
    res_id = Column('res_id', Integer)
    item_id = Column('item_id', String(255))
    url = Column('url', String)
    text = Column('text', String)
    date = Column('date', Date)
    s_date = Column('s_date', Date)
    attachments = Column('attachments', String)
    sentiment = Column('sentiment', Integer)


class PostMetrics(Model):
    __tablename__ = 'posts_metrics'

    id = Column('id', Integer, primary_key=True)
    type = Column('type', Integer)
    res_id = Column('res_id', Integer)
    url = Column('url', String)
    item_id = Column('item_id', String(255))
    date = Column('date', Date)
    s_date = Column('s_date', Date)
    likes = Column('likes', Integer)
    comments = Column('comments', Integer)
    reposts = Column('reposts', Integer)


class Accounts(Model):
    __tablename__ = "soc_accounts"

    id = Column("id", Integer, primary_key=True)
    soc_type = Column("soc_type", Integer)
    type = Column("type", String)
    work = Column("work", Integer)
    name = Column("name", String)
    login = Column("login", String)
    password = Column("password", String)
    bdate = Column("bdate", Date)
    sessionid = Column("sessionid", String)
    priority = Column("priority", Integer)
