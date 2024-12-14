import unittest
from unittest.mock import Mock, patch
import json
from aip_project import (
    get_weather_details, send_forecast,
    send_humidity, create_city_buttons
)

class TestWeatherBot(unittest.TestCase):

    @patch('aip_project.bot')
    def test_create_city_buttons(self, mock_bot):
        """Тест на проверку создания кнопок клавиатуры."""
        buttons = create_city_buttons()
        self.assertIsNotNone(buttons)
        self.assertTrue(buttons.keyboard)
        self.assertEqual(len(buttons.keyboard), 10)  # Проверка на правильное количество кнопок

    @patch('aip_project.requests.get')
    @patch('aip_project.bot')
    def test_get_weather_details_positive(self, mock_bot, mock_requests):
        """Положительный тест на получение текущей погоды."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = json.dumps({
            "main": {"temp": 15},
            "clouds": {"all": 50}
        })
        mock_requests.return_value = mock_response

        message = Mock()
        message.chat.id = 12345
        get_weather_details(message, "Москва")

        mock_bot.reply_to.assert_called_with(message, "Температура: 15\u00b0C\nОблачность: 50%")

    @patch('aip_project.requests.get')
    @patch('aip_project.bot')
    def test_get_weather_details_negative(self, mock_bot, mock_requests):
        """Негативный тест на получение текущей погоды (город не найден)."""
        mock_response = Mock()
        mock_response.status_code = 404
        mock_requests.return_value = mock_response

        message = Mock()
        message.chat.id = 12345
        get_weather_details(message, "НеизвестныйГород")

        mock_bot.reply_to.assert_called_with(message, "Город 'НеизвестныйГород' не найден. Попробуйте снова.")

    @patch('aip_project.requests.get')
    @patch('aip_project.bot')
    def test_send_forecast_positive(self, mock_bot, mock_requests):
        """Положительный тест на получение прогноза на 5 дней."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = json.dumps({
            "list": [
                {"dt_txt": "2024-01-01 12:00:00", "main": {"temp": 5}, "clouds": {"all": 30}},
                {"dt_txt": "2024-01-02 12:00:00", "main": {"temp": 6}, "clouds": {"all": 40}},
            ]
        })
        mock_requests.return_value = mock_response

        message = Mock()
        message.chat.id = 12345
        send_forecast(message, "Москва")

        expected_message = (
            "Прогноз погоды на 5 дней:\n"
            "Дата: 2024-01-01 12:00:00\nТемпература: 5\u00b0C\nОблачность: 30%\n\n"
            "Дата: 2024-01-02 12:00:00\nТемпература: 6\u00b0C\nОблачность: 40%\n\n"
        )
        mock_bot.reply_to.assert_called_with(message, expected_message)

    @patch('aip_project.requests.get')
    @patch('aip_project.bot')
    def test_send_forecast_negative(self, mock_bot, mock_requests):
        """Негативный тест на получение прогноза на 5 дней (ошибка API)."""
        mock_response = Mock()
        mock_response.status_code = 404
        mock_requests.return_value = mock_response

        message = Mock()
        message.chat.id = 12345
        send_forecast(message, "НеизвестныйГород")

        mock_bot.reply_to.assert_called_with(message, "Не удалось получить прогноз. Проверьте город.")

    @patch('aip_project.requests.get')
    @patch('aip_project.bot')
    def test_send_humidity_positive(self, mock_bot, mock_requests):
        """Положительный тест на получение влажности."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = json.dumps({"main": {"humidity": 75}})
        mock_requests.return_value = mock_response

        message = Mock()
        message.chat.id = 12345
        send_humidity(message, "Москва")

        mock_bot.reply_to.assert_called_with(message, "Влажность в городе Москва: 75%")

    @patch('aip_project.requests.get')
    @patch('aip_project.bot')
    def test_send_humidity_negative(self, mock_bot, mock_requests):
        """Негативный тест на получение влажности (город не найден)."""
        mock_response = Mock()
        mock_response.status_code = 404
        mock_requests.return_value = mock_response

        message = Mock()
        message.chat.id = 12345
        send_humidity(message, "НеизвестныйГород")

        mock_bot.reply_to.assert_called_with(message, "Город 'НеизвестныйГород' не найден. Попробуйте снова.")

if __name__ == "__main__":
    unittest.main()
