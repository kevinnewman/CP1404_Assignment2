from kivy.app import App
from kivy.lang import Builder
from kivy.core.window import Window
from kivy.properties import StringProperty
from kivy.properties import ListProperty
from io import open

import time
import currency
import trip


class CurrencyConverterApp(App):
    """ Firstly setting up some fixed variables to be passed into KV """

    current_country = StringProperty()
    country_list = ListProperty()

    current_trip_location = ()
    country = []
    country_counter = 0  # counter to show number of countries being visited in config.txt file
    country_trip_data = []  # storage array for trip data with home country stripped out
    todays_date = (time.strftime("%Y/%m/%d"))
    current_date = ('Today is:\n ' + todays_date)  # kv variable

    trip_file = open('config.txt', 'r')
    header = trip_file.read(3)  # probably not the right way to remove the BOM characters???
    home_country = trip_file.readline().strip()  # home country declared
    while True:
        line = trip_file.readline().strip()
        if not line:
            break
        country_trip_data += (line.split(','))
        country_counter += 1
    trip_file.close()

    current_trip_location_factor = 0
    for i in range(country_counter):
        if todays_date > country_trip_data[current_trip_location_factor + 1] and todays_date < country_trip_data[current_trip_location_factor + 2]:
            current_trip_location = ('Current trip location: \n' + country_trip_data[current_trip_location_factor])
        else:
            current_trip_location_factor += 3

# declares/strips country names for spinner in kv file
    conversion_factor = 0
    for i in range(country_counter):
        country.append(country_trip_data[conversion_factor])
        conversion_factor += 3
    country_list = country  # country_list - variable used by spinner

    def build(self):
        """ build the Kivy app from the kv file """
        Window.size = (350, 500)
        self.title = 'Foreign Exchange Calculator'
        self.root = Builder.load_file('gui.kv')
        self.current_country = self.country_trip_data[0]
        return self.root

    def conversion1(self):
        value = self.get_validated_amount(self.root.ids.currency_amount1.text)
        conversion1_details = self.get_details(self.root.ids.choose_country.text)
        conversion2_details = self.get_details(self.root.ids.home_country.text)
        conversion_result = format(self.convert(value, conversion1_details[1], conversion2_details[1]), '.2f')
        if conversion_result == '-1.00':
            (self.root.ids.current_conversion.text) = str('Invalid conversion')
            (self.root.ids.currency_amount2.text) = str('')
        else:
            (self.root.ids.currency_amount2.text) = str(conversion_result)
            temp_text = (conversion1_details[1] + '(' + conversion1_details[2] + ')' + ' to ' + conversion2_details[1] + '(' + conversion2_details[2] + ')')
            (self.root.ids.current_conversion.text) = str(temp_text)

    def conversion2(self):
        value = self.get_validated_amount(self.root.ids.currency_amount2.text)
        conversion1_details = self.get_details(self.root.ids.choose_country.text)
        conversion2_details = self.get_details(self.root.ids.home_country.text)
        conversion_result = format(self.convert(value, conversion2_details[1], conversion1_details[1]), '.2f')
        if conversion_result == '-1.00':
            (self.root.ids.current_conversion.text) = str('Invalid conversion')
            (self.root.ids.currency_amount1.text) = str('')
        else:
            (self.root.ids.currency_amount1.text) = str(conversion_result)
            temp_text = (conversion2_details[1] + '(' + conversion2_details[2] + ')' + ' to ' + conversion1_details[1] + '(' + conversion1_details[2] + ')')
            (self.root.ids.current_conversion.text) = str(temp_text)

    def get_validated_amount(self, currency_input_test):
        """
        get text input from text entry widget, convert to float
        :return: 0 if error, float version of text if valid
        """
        try:
            value = float(currency_input_test)
            return value
        except ValueError:
            return 0

    def get_details(self, country_name):
        file = open('currency_details.txt', encoding='utf-8')
        for line in file:
            words = [word for word in line.strip().split(',')]
            if words[0] == country_name:
                file.close()
                return tuple(words)
        file.close()
        return ('-1')

    def convert(self, amount, home_currency, target_currency):
        from web_utility import load_page

        def remove_text_before(position_string, all_text):
            remove_start = all_text.find(position_string)
            if remove_start == -1:
                return ''
            remove_start += len(position_string)
            return all_text[remove_start:]

        def remove_span(all_text):
            remove_start = all_text.find('<')
            remove_end = all_text.find('>') + 1
            return all_text[:remove_start] + all_text[remove_end:]

        format_string = 'https://www.google.com/finance/converter?a={}&from={}&to={}'
        url_string = format_string.format(amount, home_currency, target_currency)

        html_string = load_page(url_string)
        if not html_string:
            return -1

        data_string = remove_text_before('converter_result>', html_string)
        if not data_string:
            return -1

        data_string = remove_span(data_string)
        converted_amount_string = remove_text_before(" = ", data_string)
        if not converted_amount_string:
            return -1

        end_amount = converted_amount_string.find(' ')
        return float(converted_amount_string[:end_amount])

CurrencyConverterApp().run()
