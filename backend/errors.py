class ModuleNotReadyError(NotImplementedError):
    """Identify an intentionally unfinished team module."""

    def __init__(self, module: str):
        self.module = module
        super().__init__(f"Module '{module}' is pending implementation by the team.")
