from sqlalchemy import String, Column, Integer, Date
from sqlalchemy.ext.declarative import declarative_base

Model = declarative_base(name='Model')


class Resources(Model):
    """
        representation of table `resources`, database server is 94.247.131.121
    """
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
    """
        representation of table `sub_follow`, database server is 94.247.131.121, database name is `fb_candy`
    """
    __tablename__ = 'sub_follow'

    id = Column('id', Integer, primary_key=True)
    type = Column('type', Integer)
    res_id = Column('res_id', Integer)
    sf_type = Column('sf_type', String(255))
    count = Column('count', Integer)
    date = Column('date', Date)


class Posts(Model):
    """
        representation of table `res_posts`, database server is 94.247.131.121, database name is `fb_candy`
    """
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
    """
        representation of table `posts_metrics`, database server is 94.247.131.121, database name is `fb_candy`
    """
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
    """
        representation of table `soc_accounts`, database server is 94.247.131.122, database name is `social_services`
    """
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


class Tokens(Model):
    """
        representation of table `twitter_tokens`, database server is 94.247.131.121, database name is `fb_candy`
    """
    __tablename__ = "twitter_tokens"

    id = Column("id", Integer, primary_key=True)
    bearer_token = Column("bearer_token", String)
    access_token = Column("access_token", String)
    access_token_secret = Column("access_token_secret", String)
    api_key = Column("api_key", String)
    api_key_secret = Column("api_key_secret", String)
    requests = Column("requests", Integer)
    requests_limit = Column("requests_limit", Integer)


class Proxy(Model):
    """
        representation of table `proxies`, database server is 94.247.130.52, database name is `recognition_service`
        *Do not ask me, why recognition_service. Shit happens*
    """
    __tablename__ = "proxies"

    id = Column("id", Integer, primary_key=True)
    proxy = Column("proxy", String)
    port = Column("port", String)
    login = Column("login", String)
    password = Column("password", String)
    use_date = Column("use_date", Date)
    expiry_date = Column('expiry_date', Date)
    script = Column("script", String)
    error = Column("error", String)
    status = Column("status", Integer)
