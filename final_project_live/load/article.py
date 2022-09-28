from sqlalchemy import Column, String, Integer

from base import Base

# > We're creating a class called `Article` that inherits from `Base` (which is a class that comes
# from the `sqlalchemy` library). This class will be used to create objects that will be stored in a
# database
class Article(Base):
    __tablename__ = 'articles'

    id = Column(String, primary_key=True)   
    body = Column(String)
    host = Column(String)
    title = Column(String)
    newspaper_uid = Column(String)
    n_tokens_body = Column(Integer)
    n_tokens_title = Column(Integer)
    url = Column(String, unique=True)

    def __init__(self, uid, body, host, newspaper_uid, n_tokens_body, n_tokens_title, title, url):
        """
        It takes in a bunch of parameters and assigns them to the object
        
        :param uid: unique identifier for the article
        :param body: The text of the article
        :param host: the host of the article
        :param newspaper_uid: The unique identifier of the newspaper in which the article was published
        :param n_tokens_body: Number of words in the content
        :param n_tokens_title: Number of words in the title
        :param title: The title of the article
        :param url: The url of the article
        """
        self.id = uid
        self.body = body
        self.host = host
        self.newspaper_uid = newspaper_uid
        self.n_tokens_body = n_tokens_body
        self.n_tokens_title = n_tokens_title
        self.title = title
        self.url = url