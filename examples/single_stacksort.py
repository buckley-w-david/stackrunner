from datetime import datetime
import stackrunner
config = stackrunner.RunnerConfig(
    tags=["python", "sorting"],
    not_tags=["python-2.x"],
    safety_date=datetime(2020, 10, 17),
    signature=stackrunner.Signature(
        arguments=1,
    )
)
import logging
stackrunner.logger.setLevel(level=logging.DEBUG)
logging.basicConfig()
stackrunner.init(config)

from random import shuffle
l = list(range(100))
shuffle(l)

from stackrunner import quicksort
print(quicksort(l))
