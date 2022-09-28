import argparse
import hashlib
import logging
logging.basicConfig(level=logging.INFO)
import nltk

from urllib.parse import urlparse
from nltk.corpus import stopwords

import pandas as pd

stop_words = set(stopwords.words('spanish'))
logger = logging.getLogger(__name__)


def main(filename):
    """
    It reads a dataframe, adds a newspaper_uid column, extracts the host, fills missing titles,
    generates uids for each row, removes new lines from the body, tokenizes the title and body, removes
    duplicate entries, and drops rows with missing values
    
    :param filename: The name of the file to be cleaned
    :return: The dataframe
    """
    logger.info('Starting cleaning process')

    df = _read_data(filename)
    newspaper_uid = _extract_newspaper_uid(filename)
    df = _add_newspaper_uid_column(df, newspaper_uid)
    df = _extract_host(df)
    df = _fill_missing_titles(df)
    df = _generate_uids_for_rows(df)
    df = _remove_new_lines_from_body(df)
    df = _tokenize_title(df)
    df = _tokenize_body(df)
    df = _remove_duplicate_entries(df,'title')
    df = _drop_rows_with_missing_values(df)
    _save_data(df, filename)

    return df


def _read_data(filename):
    """
    > This function reads a CSV file and returns a Pandas DataFrame
    
    :param filename: The name of the file to read
    :return: A dataframe
    """
    logger.info('Reading file {}'.format(filename))

    return pd.read_csv(filename, encoding = 'utf-8-sig')


def _extract_newspaper_uid(filename):
    """
    > It takes a filename as input and returns the newspaper uid
    
    :param filename: the name of the file that we are going to process
    :return: The first part of the filename, which is the newspaper uid.
    """
    logger.info('Extracting newspaper uid')
    newspaper_uid = filename.split('_')[0]  

    logger.info('Newspaper uid detected: {}'.format(newspaper_uid))
    return newspaper_uid


def _add_newspaper_uid_column(df, newspaper_uid):
    """
    It adds a new column to the dataframe, called newspaper_uid, and fills it with the value of the
    newspaper_uid parameter
    
    :param df: the dataframe we're going to add the column to
    :param newspaper_uid: The unique identifier of the newspaper
    :return: The dataframe with the new column added.
    """
    logger.info('Filling newspaper_uid column with {}'.format(newspaper_uid))
    df['newspaper_uid'] = newspaper_uid

    return df


def _extract_host(df):
    """
    It takes a dataframe as input, and returns a dataframe with a new column called 'host' that contains
    the hostname of the url
    
    :param df: The dataframe to be processed
    :return: The host of the url.
    """
    logger.info('Extracting host from urls')
    df['host'] = df['url'].apply(lambda url: urlparse(url).netloc)

    return df


def _fill_missing_titles(df):
    """
    > We're going to extract the last part of the URL, split it on the hyphen, and join it back together
    with spaces
    
    :param df: The dataframe to be cleaned
    :return: A dataframe with the missing titles filled in.
    """
    logger.info('Filling missing titles')
    missing_titles_mask = df['title'].isna()

    missing_titles = (df[missing_titles_mask]['url']
                        .str.extract(r'(?P<missing_titles>[^/]+)$')
                        .applymap(lambda title: title.split('-'))
                        .applymap(lambda title_word_list: ' '.join(title_word_list))
                        )
    
    df.loc[missing_titles_mask, 'title'] = missing_titles.loc[:, 'missing_titles']

    return df


def _generate_uids_for_rows(df):
    """
    It takes a dataframe, generates a hash for each row, and adds it to the dataframe
    
    :param df: The dataframe to be processed
    :return: A dataframe with the uid column added and set as the index
    """
    logger.info('Generating uids for each row')
    uids = (df
            .apply(lambda row: hashlib.md5(bytes(row['url'].encode())), axis=1)
            .apply(lambda hash_object: hash_object.hexdigest())
            )
    df['uid'] = uids
    return df.set_index('uid')


def _remove_new_lines_from_body(df):
    """
    > We're going to take the body column, turn it into a list of characters, replace new lines with
    spaces, and then turn it back into a string
    
    :param df: The dataframe to be cleaned
    :return: A dataframe with the body column stripped of new lines.
    """
    logger.info('Removing new lines from body')

    stripped_body = (df
                        .apply(lambda row: row['body'], axis=1)
                        .apply(lambda body: list(body))
                        .apply(lambda letters: list(map(lambda letter: letter.replace('\n',' '), letters)))
                        .apply(lambda letters: ''.join(letters))
                    )
    df['body'] = stripped_body

    return df


def _tokenize_column(df, column_name):
    """
    - Drop all rows with missing values
    - Tokenize the column
    - Filter out non-alphabetic tokens
    - Lowercase all tokens
    - Filter out stop words
    - Count the remaining tokens
    
    :param df: the dataframe
    :param column_name: The name of the column you want to tokenize
    :return: A series of the number of words in each row of the column.
    """
    return (df
                .dropna()
                .apply(lambda row: nltk.word_tokenize(row[column_name]), axis=1)
                .apply(lambda tokens: list(filter(lambda token: token.isalpha(), tokens)))
                .apply(lambda tokens: list(map(lambda token: token.lower(), tokens)))
                .apply(lambda word_list: list(filter(lambda word: word not in stop_words, word_list)))
                .apply(lambda valid_word_list: len(valid_word_list))
            )


def _tokenize_title(df):
    """
    It takes a dataframe and a column name, and returns a new column with the number of tokens in the
    column
    
    :param df: the dataframe
    :return: The number of tokens in the title column.
    """
    df['n_tokens_title'] = _tokenize_column(df, 'title')
    return df


def _tokenize_body(df):
    """
    It takes a dataframe and a column name, and returns a new dataframe with a new column called
    `n_tokens_<column_name>` that contains the number of tokens in the column
    
    :param df: the dataframe
    :return: The number of tokens in the body of the article.
    """
    df['n_tokens_body'] = _tokenize_column(df, 'body')
    return df


def _remove_duplicate_entries(df,column_name):
    """
    This function removes duplicate entries from the dataframe
    
    :param df: The dataframe to be cleaned
    :param column_name: The name of the column that you want to remove duplicates from
    :return: The dataframe with the duplicate entries removed.
    """
    logger.info('Removing duplicate entries')
    df.drop_duplicates(subset=[column_name], keep='first', inplace=True)

    return df


def _drop_rows_with_missing_values(df):
    """
    > Drop rows with missing values
    
    :param df: The dataframe to be cleaned
    :return: A dataframe with no missing values
    """
    logger.info('Dropping rows with missing values')
    return df.dropna()


def _save_data(df, filename):
    """
    > The function takes in a dataframe and a filename, and saves the dataframe to a file with the name
    `clean_<filename>`
    
    :param df: The dataframe to be saved
    :param filename: The path to the CSV file containing the data
    """
    clean_filename = 'clean_{}'.format(filename)
    logger.info('Saving data at location: {}'.format(filename))
    df.to_csv(clean_filename, encoding = 'utf-8-sig')


# A way to run the script from the command line.
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('filename', help='The path to the dirty data', type=str)

    args = parser.parse_args()

    df = main(args.filename)
    print(df)