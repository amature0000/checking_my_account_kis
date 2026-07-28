import functools

class Logger:
    class_name = None
    func_name = None

    @staticmethod
    def printstack(func, should_print):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            instance = args[0] if args else None
            Logger.class_name = instance.__class__.__name__ if hasattr(instance, "__class__") else func.__module__
            Logger.func_name = func.__name__
            if should_print:
                print(f"[{Logger.class_name}] called {Logger.func_name}")
            return func(*args, **kwargs)
        return wrapper

    @staticmethod
    def apply_to_all_methods(decorator):
        def decorate(cls):
            for name, attr in cls.__dict__.items():
                if name.startswith("__"):
                    continue

                should_print = not name.startswith("_")
                if isinstance(attr, staticmethod):
                    setattr(cls, name, staticmethod(decorator(attr.__func__, should_print=should_print)))
                elif isinstance(attr, classmethod):
                    setattr(cls, name, classmethod(decorator(attr.__func__, should_print=should_print)))
                elif callable(attr):
                    setattr(cls, name, decorator(attr, should_print=should_print))
            return cls
        return decorate
    
    @classmethod
    def log(cls, message:str):
        print(f"[{cls.class_name}] {cls.func_name}: {message}")
