import argparse
import logging
logging.basicConfig(level=logging.INFO)

import pandas as pd

from article import Article
from base import Base, Engine, Session

logger = logging.getLogger(__name__)


def main(filename):
    """
    We are creating a session to our database, and then iterating over our dataframe to create a new
    Article object for each row, and then adding that object to the session, and then committing the
    session
    
    :param filename: The path to the CSV file with the articles
    """
    Base.metadata.create_all(Engine)
    session = Session()
    articles = pd.read_csv(filename)

    for index, row in articles.iterrows():
        logger.info('Loading article uid {} into DB'.format(row['uid']))
        article = Article(row['uid'], row['body'], row['host'], row['newspaper_uid'], row['n_tokens_body'], row['n_tokens_title'], row['title'], row['url'])
        session.add(article)

    session.commit()
    session.close()



# This is a way to make sure that the code is only executed when the file is run directly.
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('filename', help='The file you want to load into the db', type=str)

    args = parser.parse_args()
    main(args.filename)