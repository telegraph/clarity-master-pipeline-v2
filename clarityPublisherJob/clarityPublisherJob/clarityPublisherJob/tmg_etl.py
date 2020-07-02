import abc
from abc import ABCMeta
import os

GOOGLE_APP_CREDENTIALS_ENV_NAME = 'GOOGLE_APPLICATION_CREDENTIALS'
GOOGLE_CREDENTIALS_PATH = '/google-keys/'


class TMGETL(metaclass=ABCMeta):
    """
    Skeleton of a generic ETL pipeline.

    This class take care of parsing and loading environment and arguments

    A concrete ETL MUST inherit from this class and implements the 3 abstract
    methods

     def pre_execution_cleansing(self):
        pass

     def pipeline(self)
        pass

     def post_execution_cleanup(self):
        pass

    This methods are called by the execute() method and they run in sequence.

    """
    # added this back as cannot see another way to authenticate 
    def __init__(self):

        if not os.environ.get(GOOGLE_APP_CREDENTIALS_ENV_NAME):
            os.environ[GOOGLE_APP_CREDENTIALS_ENV_NAME] = GOOGLE_CREDENTIALS_PATH + 'dev-pipeline.json'

    @property
    @abc.abstractmethod
    def logger(self):
        pass

    def pre_execution_cleansing(self):
        pass

    @abc.abstractmethod
    def pipeline(self):
        pass

    def post_execution_cleanup(self):
        pass

    def execute(self):
        """
        Execute the ETL pipeline
        """

        try:
            self.pre_execution_cleansing()
            self.pipeline()
        except Exception as ex:
            self.logger.critical('Pipeline Failure! {}'.format(ex))
            raise ex
        finally:
            self.post_execution_cleanup()
