import datetime
import typing

from bs4 import BeautifulSoup
from stackapi import StackAPI

from stackrunner._meta import config


'''
Pass this as key when making requests against the Stack Exchange API to receive a higher request quota.

This is not considered a secret, and may be safely embed in client side code or distributed binaries.
'''
APP_KEY='i1jWtawQVUugZZgFSlTlTg(('

StackOverflowApi = StackAPI('stackoverflow', key=APP_KEY)
StackOverflowApi.page_size = 50
StackOverflowApi.max_pages = 1

def fetch_code(keyword: str, config: config.RunnerConfig) -> typing.Generator[str, None, None]:
    question_options = {
        'order': 'desc',
        'sort': 'relevance',
        'q': keyword,
        'nottagged': config.not_tags,
        'tagged': config.tags,
        'filter': '!b93xdWqUwqOO7m'
    }
    answer_options = {
        'order': 'desc',
        'sort': 'votes',
        'filter': '-XG6tqDiasfBQHS1'
    }
    if config.safety_date:
        question_options['todate'] = config.safety_date
        answer_options['todate'] = config.safety_date

    question_search = { 'has_more': True }
    answer_search = { 'has_more': True }

    question_page = 1
    while question_search.get('has_more', False):
        question_search = StackOverflowApi.fetch('search/advanced', page=question_page, **question_options)
        question_page = question_search['page']+1

        ids = [ item['question_id'] for item in question_search['items'] if item['is_answered'] ]

        answer_page = 1
        while answer_search.get('has_more', False):
            answer_search = StackOverflowApi.fetch('questions/{ids}/answers', ids=ids, page=answer_page, **answer_options)
            answer_page = answer_search['page']+1

            for answer in answer_search['items']:
                if config.safety_date:
                    edit_date = datetime.datetime.fromtimestamp(answer.get('last_edit_date', 0))
                    if edit_date > config.safety_date:
                        continue
                soup = BeautifulSoup(answer['body'], features="lxml")
                for code in soup.find_all('code'):
                    yield code.text
