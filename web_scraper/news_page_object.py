import bs4
import requests

from common import config


# > This class is used to represent a news page.
class NewsPage:

    def __init__(self, news_site_uid, url):
        """
        It takes the news_site_uid and url as parameters, and then it sets the _config and _queries
        attributes to the values of the news_site_uid key in the config dictionary, and then it sets the
        _html and _url attributes to None and url, respectively
        
        :param news_site_uid: The unique identifier for the news site
        :param url: The url of the article we want to extract
        """
        self._config = config()['news_sites'][news_site_uid]
        self._queries = self._config['queries']
        self._html = None
        self._url = url

        self._visit(url)


    def _select(self, query_string):
        """
        The function takes a query string as an argument and returns a list of all the elements that
        match the query string
        
        :param query_string: The CSS selector to search for
        :return: A list of elements that match the query string.
        """
        return self._html.select(query_string)


    def _visit(self, url):
        """
        The function takes a url as an argument, makes a request to that url, and then parses the
        response using BeautifulSoup
        
        :param url: The URL of the page to download
        """
        headers = {'User-Agent': 'Chrome/51.0.2704.103 Safari/537.36'}
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        self._html = bs4.BeautifulSoup(response.text, 'html.parser')


# It's a subclass of NewsPage, and it overrides the article_links method
class HomePage(NewsPage):

    def __init__(self, news_site_uid, url):
        """
        The __init__ function is a constructor that initializes the class with the parameters passed to
        it
        
        :param news_site_uid: The unique identifier for the news site
        :param url: The url of the article we want to extract
        """
        super().__init__(news_site_uid, url)


    @property
    def article_links(self):
        """
        It takes the list of links from the homepage, and returns a set of links that are unique.
        :return: A set of links to articles on the homepage.
        """
        link_list = []
        for link in self._select(self._queries['homepage_article_links']):
            if link and link.has_attr('href'):
                link_list.append(link)
        return set(link['href'] for link in link_list)


# It's a class that represents an article page
class ArticlePage(NewsPage):

    def __init__(self, news_site_uid, url):
        """
        The __init__ function is a constructor that initializes the class with the parameters passed to it.
        
        :param news_site_uid: The unique identifier for the news site
        :param url: The url of the article we want to extract
        """
        super().__init__(news_site_uid, url)


    @property
    def body(self):
        """
        It returns the body of the article
        :return: The body of the article.
        """
        result = self._select(self._queries['article_body'])
        return result[0].text if len(result) else ''
    
    @property
    def title(self):
        """
        It returns the title of the article
        :return: The title of the article.
        """
        result = self._select(self._queries['article_title'])
        return result[0].text if len(result) else ''

    @property
    def url(self):
        """
        It returns the url of the object.
        :return: The url of the object
        """
        return self._url