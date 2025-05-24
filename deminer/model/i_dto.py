class IDto:
    def __init__(self, **props):
        for key, value in props.items():
            setattr(self, key, value)

    def put_into_dto(self):
        return {
            attribute: value for attribute, value in self.__dict__.items() if not attribute.startswith("_")
        }