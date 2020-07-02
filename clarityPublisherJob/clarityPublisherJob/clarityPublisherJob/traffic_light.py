from threading import Lock

lock = Lock()


class TrafficLight(object):

    @staticmethod
    def block(logger):
        """
        Used from different threads to allow concurrency on operations that are not parallelizable.
        This is used to reserve the resource until release i called.
        :return:
        """

        lock.acquire()
        logger.info("LOCK: acquired")

    @staticmethod
    def release(logger):
        """
        Release the resource so another thread can take it using block.
        :return:
        """

        lock.release()
        logger.info("LOCK: released")
