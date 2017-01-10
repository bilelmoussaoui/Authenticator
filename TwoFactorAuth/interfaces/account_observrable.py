from TwoFactorAuth.interfaces.observable import Observable

class AccountObservable(Observable):

    def update_observers(self, *args, **kwargs):
        for observer in self.observers:
            observer.update(*args, **kwargs)

class AccountRowObservable(Observable):

    def update_observers(self, *args, **kwargs):
        for observer in self.observers:
            observer.update(*args, **kwargs)
