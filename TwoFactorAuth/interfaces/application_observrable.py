from TwoFactorAuth.interfaces.observable import Observable

class ApplicaitonObservable(Observable):

    def update_observers(self, *args, **kwargs):
        for observer in self.observers:
            observer.update(*args, **kwargs)
