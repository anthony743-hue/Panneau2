class ApplicationError(Exception):
    pass


class DataAccessError(ApplicationError):
    pass


class ModelePanneauLoadError(DataAccessError):
    pass


class ModelePanneauPersistenceError(DataAccessError):
    pass
