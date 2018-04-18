class DBRouter:
    def db_for_read(self, model, **hints):
        if model._meta.app_label == 'ticker_app':
            return 'portal_ticker'
        return None

    def db_for_write(self, model, **hints):
        if model._meta.app_label == 'ticker_app':
            return 'portal_ticker'
        return None

    def allow_relation(self, obj1, obj2, **hints):
        if obj1._meta.app_label == 'ticker_app' and obj2._meta.app_label == 'ticker_app':
            return True
        elif 'ticker_app' not in [obj1._meta.app_label, obj2._meta.app_label]:
            return None
        return False

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        if app_label == 'ticker_app':
            return db == 'portal_ticker'
        elif db == 'portal_ticker':
            return False
        return None


class PrimaryRouter:
    def db_for_read(self, model, **hints):
        return 'default'

    def db_for_write(self, model, **hints):
        return 'default'

    def allow_relation(self, obj1, obj2, **hints):
        db_list = ('default',)
        if obj1._state.db in db_list and obj2._state.db in db_list:
            return True
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        return True
