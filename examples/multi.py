import stackrunner
# Handle imports to stackrunner.sort
sort_config = stackrunner.RunnerConfig(
    tags=["python", "sorting"],
    not_tags=["python-2.x"],
    signature=stackrunner.Signature(
        arguments=1
    ),
    prefix='sort'
)
# Handle imports to stackrunner.search
search_config = stackrunner.RunnerConfig(
    tags=["python", "search"],
    not_tags=["python-2.x"],
    signature=stackrunner.Signature(
        arguments=2
    ),
    prefix='search'
)
stackrunner.init(sort_config)
stackrunner.init(search_config)

from functools import total_ordering
@total_ordering
class DataNode:
    def __init__(self, value):
        self.value = value
        self.other_data = id(self)

    def __lt__(self, other):
        if hasattr(other, "value"):
            return self.value < other.value
        return self.value < other

    def __eq__(self, other):
        if hasattr(other, "value"):
            return self.value == other.value
        return self.value == other

from random import shuffle
l = [DataNode(i) for i in range(100)]
shuffle(l)

import logging
from stackrunner import logger
logger.setLevel(logging.DEBUG)
logging.basicConfig()

from stackrunner.search import binary_search
from stackrunner.sort import quicksort

sorted_list = quicksort(l)
index = binary_search(sorted_list, 15)
result = sorted_list[index]
print(result.value, result.other_data)
