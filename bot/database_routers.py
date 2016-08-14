__author__ = 'nasim'

class AuthRouter(object):
    """
    A router to control all database operations on models in the
    auth application.
    """
    def db_for_read(self, model, **hints):
        """
        Attempts to read auth models go to auth_db.
        """
        if model._meta.app_label == 'News':
            return 'news_db'
        return None

    def db_for_write(self, model, **hints):
        """
        Attempts to write auth models go to auth_db.
        """
        if model._meta.app_label == 'News':
            return 'news_db'
        return None

    def allow_relation(self, obj1, obj2, **hints):
        pass

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        pass