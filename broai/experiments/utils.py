import functools
import warnings

class experiment:
    default_message = "You're using an experimental module, which is subject to change in future."

    def __init__(self, message=None):
        self.message = message or self.default_message

    def __call__(self, func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            warnings.warn(
                f"[EXPERIMENT] {self.message}: {func.__name__}",
                category=UserWarning,
                stacklevel=2
            )
            return func(*args, **kwargs)
        return wrapper

    def __class_getitem__(cls, _):  # For typing support (optional)
        return cls

    @classmethod
    def __class_call__(cls, func):
        # Used when called like @experiment with no parentheses
        return cls()(func)

    def __new__(cls, *args, **kwargs):
        if len(args) == 1 and callable(args[0]) and not kwargs:
            # Handles: @experiment with no ()
            return cls().__call__(args[0])
        return super().__new__(cls)

    @classmethod
    def message(cls, custom_message):
        return cls(message=custom_message)
