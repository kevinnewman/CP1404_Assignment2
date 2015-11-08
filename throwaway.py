from kivy.app import App
from kivy.lang import Builder
from kivy.core.window import Window
from kivy.properties import StringProperty
from kivy.properties import ListProperty
from io import open

import time

class CurrencyConverterApp(App):
    """ Firstly setting up some fixed variables to be passed into KV """

    current_country = StringProperty()
    country_list = ListProperty()
    current_trip_location = ()

    country_error = ()
    country_counter = 0  # counter to show number of countries being visited in config.txt file
    country_trip_data = []  # storage array for trip data with home country stripped out

    def build(self):
        """ build the Kivy app from the kv file """
        Window.size = (350, 500)
        self.title = 'Foreign Exchange Calculator'
        self.root = Builder.load_file('gui.kv')

        country_counter = 0  # counter to show number of countries being visited in config.txt file
        country_trip_data = []  # storage array for trip data with home country stripped out
        todays_date = (time.strftime("%Y/%m/%d"))
        (self.root.ids.current_date.text) = ('Today is:\n ' + todays_date)  # kv variable

        trip_file = open('config.txt', 'r')
        discard_header = trip_file.read(3)  # probably not the right way to remove the BOM characters???
        home_country = trip_file.readline().strip()  # home country declared
        while True:
            line = trip_file.readline().strip()
            if not line:
                break
            line = (line.split(','))
            country_test = self.get_details(line[0])

            new_date1 = time.strptime((line[1]), "%Y/%m/%d")
            new_date2 = time.strptime((line[2]), "%Y/%m/%d")
            if country_test == ():
                self.country_error = line[0]
                (self.root.ids.current_conversion.text) = ('Invalid country name:\n' + line[0])
            elif new_date1 > new_date2:
                print('dates are wrong ' + (line[1]))
                (self.root.ids.current_conversion.text) = ('Invalid dates:\n' + (line[1]) + '\n' + (line[2]))
            else:
                country_trip_data += line
                country_counter += 1
        trip_file.close()

        current_trip_location_factor = 0
        for i in range(country_counter):
            date = time.strptime((todays_date), "%Y/%m/%d")
            date1 = time.strptime(country_trip_data[current_trip_location_factor + 1], "%Y/%m/%d")
            date2 = time.strptime(country_trip_data[current_trip_location_factor + 2], "%Y/%m/%d")
            if date > date1 and date < date2:
                (self.root.ids.current_trip_location.text) = ('Current trip location: \n' + country_trip_data[current_trip_location_factor])
            else:
                current_trip_location_factor += 3
        if self.country_error == ():
            (self.root.ids.current_conversion.text) = str('Trip details accepted')

# test for valid home country
        country_test = self.get_details(home_country)
        if country_test != ():
            (self.root.ids.home_country.text) = home_country
        else:
            (self.root.ids.current_conversion.text) = ('Invalid country name:\n' + home_country)

# declares/strips country names for spinner in kv file
        country = []
        conversion_factor = 0
        for i in range(country_counter):
            country.append(country_trip_data[conversion_factor])
            conversion_factor += 3
        self.country_list = country  # country_list - variable used by spinner
        self.current_country = country_trip_data[0]

        return self.root

    def conversion1(self):
        try:
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
        except:
            pass

    def conversion2(self):
        try:
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
        except:
            pass

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
        return ()

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
