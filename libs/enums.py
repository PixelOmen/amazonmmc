class WorkTypes:
    UNKNOWN = 0
    EPISODIC = 1
    FEATURE = 2

    def __init__(self):
        raise NotImplementedError("Can't instantiate WorkTypes Enum")

    @staticmethod
    def get_int(userstr: str) -> int:
        userstr = userstr.upper()
        try:
            return getattr(WorkTypes, userstr)
        except AttributeError:
            raise AttributeError(f"Type does not exist in WorkTypes Enum: {userstr}")
    
    @staticmethod
    def get_str(userint: int) -> str:
        for k,v in WorkTypes.__dict__.items():
            if v == userint:
                return k
        raise AttributeError(f"WorkTypes Enum does not exist: {userint}")