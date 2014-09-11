
class Resource(object):
    client = None

    @classmethod
    def create(cls, *args, **kwargs):
        """
        :param args:
        :param kwargs:
        :return:
        """
        raise NotImplemented

    @classmethod
    def list(cls, *args, **kwargs):
        """

        :param args:
        :param kwargs:
        :return:
        """
        raise NotImplemented

    @classmethod
    def get(cls, *args, **kwargs):
        """

        :param args:
        :param kwargs:
        :return:
        """
        raise NotImplemented
