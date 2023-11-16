class NotOkException(Exception):
    pass


class Result:
    _status: bool
    _value: None

    def __init__(self):
        self._status = False
        self._value = None

    def ok(self):
        if self._status == False:
            raise NotOkException("Result is Not Ok")

        return self._value

    def force_ok(self):
        return self._value

    def else_err(self, err_handler: callable):
        if self._status == False:
            return err_handler()

        return self._value
    
    def is_err(self):
        if self._status == False:
            return True

        return False


class ResultBuilder:
    def __init__(self):
        # TODO : Complete function
        pass

    class FieldBuilder:
        _result = Result()

        def __init__(self, result):
            self._result = result

        def value(self, value):
            self._result._value = value
            return self

        def build(self):
            return self._result

    @classmethod
    def ok(cls):
        result = Result()
        result._status = True
        return cls.FieldBuilder(result)

    @classmethod
    def err(cls):
        result = Result()
        result._status = False
        return cls.FieldBuilder(result)
