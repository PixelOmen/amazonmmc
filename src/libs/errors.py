class JSONParsingError(Exception):
    def __init__(self, msg: str) -> None:
        super().__init__(msg)

class ResourceError(Exception):
    def __init__(self, unknowns: list[str]=..., msg: str=...) -> None:
        if unknowns is not ...:
            finalmsg = "\n"
            for unknown in unknowns:
                if msg is not ...:
                    finalmsg += f"{msg}{unknown}\n"
                else:
                    finalmsg += f"Unknown Resource: {unknown}\n"
        elif msg is not ...:
            finalmsg = msg
        else:
            finalmsg = ""
        super().__init__(finalmsg)