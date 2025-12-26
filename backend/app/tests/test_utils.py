"""Юнит-тесты для утилитарных функций"""
import pytest

from backend.app.core.utils import camel_case_to_snake_case



class TestCaseConverter:
    """Тесты для конвертации camelCase в snake_case"""

    def test_simple_camel_case(self):
        """Простой camelCase"""
        assert camel_case_to_snake_case("SomeSDK") == "some_sdk"

    def test_single_word(self):
        """Одно слово с заглавными буквами"""
        assert camel_case_to_snake_case("User") == "user"

    def test_multiple_words(self):
        """Несколько слов в camelCase"""
        assert camel_case_to_snake_case("UserProfileAPI") == "user_profile_api"

    def test_acronym_at_beginning(self):
        """Акроним в начале слова"""
        assert camel_case_to_snake_case("XMLParser") == "xml_parser"

    def test_acronym_in_middle(self):
        """Акроним в середине слова"""
        assert camel_case_to_snake_case("RServoDrive") == "r_servo_drive"

    def test_acronym_at_end(self):
        """Акроним в конце слова"""
        assert camel_case_to_snake_case("HTTPServer") == "http_server"

    def test_multiple_acronyms(self):
        """Несколько акронимов подряд"""
        assert camel_case_to_snake_case("JSONAPIResponse") == "json_api_response"

    def test_empty_string(self):
        """Пустая строка"""
        assert camel_case_to_snake_case("") == ""

    def test_already_snake_case(self):
        """Уже snake_case"""
        assert camel_case_to_snake_case("already_snake") == "already_snake"

    def test_mixed_case(self):
        """Смешанный регистр"""
        assert camel_case_to_snake_case("MixedCaseExample") == "mixed_case_example"

    def test_numbers_in_name(self):
        """С цифрами в названии"""
        assert camel_case_to_snake_case("User2FA") == "user_2fa"
        assert camel_case_to_snake_case("APIv2") == "api_v2"

    @pytest.mark.parametrize("input_str, expected", [
        ("SomeSDK", "some_sdk"),
        ("UserAPI", "user_api"),
        ("RESTfulAPI", "restful_api"),
        ("OAuth2", "o_auth_2"),
        ("IDGenerator", "id_generator"),
        ("PDFConverter", "pdf_converter"),
    ])
    def test_parametrized_cases(self, input_str, expected):
        """Параметризованные тесты для разных случаев"""
        result = camel_case_to_snake_case(input_str)
        assert result == expected, f"Ожидалось {expected}, получено {result}"