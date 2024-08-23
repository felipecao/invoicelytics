import logging

from invoicelytics.run import create_app


class BaseService:

    def _run(self, *args, **kwargs):
        raise NotImplementedError("Run method must be implemented in the subclass.")

    def execute(self, *args, **kwargs):
        try:
            with create_app().app_context():
                return self._run(*args, **kwargs)
        except Exception as e:
            logging.error(f"Error while executing service, error: {e}")
            raise e
