import datetime
import sys

import logging
logger = logging.getLogger(__name__)

from stackrunner._meta import injector
from stackrunner._meta.config import RunnerConfig, Signature

def init(runner_config):
    loader = injector.StackRunnerLoader(runner_config)
    finder = injector.StackRunnerFinder(loader, runner_config)
    finder.inject()
