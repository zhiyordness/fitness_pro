import logging


class UserContextFilter(logging.Filter):

    def filter(self, record):
        if not hasattr(record, "user_id"):
            record.user_id = "-"

        return True

