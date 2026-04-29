from .base import PaymeError


class Errors:
    @staticmethod
    def parse_error(lang="ru"):
        return PaymeError(-32700, lang)

    @staticmethod
    def invalid_request(lang="ru"):
        return PaymeError(-32600, lang)

    @staticmethod
    def method_not_found(lang="ru"):
        return PaymeError(-32601, lang)

    @staticmethod
    def invalid_params(lang="ru"):
        return PaymeError(-32602, lang)

    @staticmethod
    def internal(lang="ru"):
        return PaymeError(-32400, lang)

    @staticmethod
    def invalid_account(lang="ru"):
        return PaymeError(-31050, lang)

    @staticmethod
    def invalid_amount(lang="ru"):
        return PaymeError(-31001, lang)

    @staticmethod
    def transaction_not_found(lang="ru"):
        return PaymeError(-31003, lang)

    @staticmethod
    def transaction_exists(lang="ru"):
        return PaymeError(-31008, lang)

    @staticmethod
    def unable_to_perform(lang="ru"):
        return PaymeError(-31060, lang)

    @staticmethod
    def unable_to_cancel(lang="ru"):
        return PaymeError(-31007, lang)
    
    @staticmethod
    def access_denied(lang="ru"):
        return PaymeError(-32504, lang)
    
    @staticmethod
    def transaction_in_progress(lang="ru"):
        return PaymeError(-31099, lang)