from os import path


class BaseNotification(object):
    slug = None
    name = None
    frequency = None
    subject_template = None

    @classmethod
    def body_template(cls):
        return path.join(cls.__module__.split('.')[0], 'notifications',
                         "%s_body.html" % cls.slug)

    @classmethod
    def subject_template(cls):
        return path.join(cls.__module__.split('.')[0], 'notifications',
                         "%s_subject.txt" % cls.slug)
