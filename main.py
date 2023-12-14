from collections import UserDict
import re
from datetime import datetime


class Field:  # Базовий клас для полів запису.
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)


class Name(Field):  # Клас для зберігання імені контакту.
    pass


class Phone(Field):  # Клас для зберігання номера телефону.
    def __init__(self, value):
        super().__init__(self.validate(value))

    @staticmethod
    def validate(value):
        if value.isdigit() and len(value) == 10:
            return value
        else:
            raise ValueError('phone number must contain 10 digits')


class Birthday(Field):
    def __init__(self, value):
        super().__init__(self.validate_date_of_birth(value))

    @staticmethod  # перевірка дати
    def validate_date_of_birth(value):
        pattern = re.compile(r'^(\d{4}[- /.]\d{1,2}[- /.]\d{1,2}|\d{1,2}[- /.]\d{1,2}[- /.]\d{4})$')
        if bool(pattern.match(value)):
            return Birthday.parse_date(value)
        else:
            raise ValueError('the date format must match (yyyy mm dd),(dd mm yyyy)')

    @staticmethod  # створеня обекту datetime
    def parse_date(date_string):
        parts = re.split(r'[ ,.]', date_string)
        current_date = datetime.now()

        if len(parts[0]) == 4:
            year, month, day = parts
        else:
            day, month, year = parts

        birthdate = datetime(int(year), int(month), int(day))

        if current_date >= birthdate:
            return birthdate.date()
        else:
            raise ValueError('date of birth is greater than the current date')


class Record:  # Клас для зберігання інформації про контакт
    def __init__(self, name, birthday=None):
        self._name = Name(name)
        self._phones = []
        if birthday is not None:
            self._birthday = self.__add_birthday(birthday)
        else:
            self._birthday = None

    def __add_birthday(self, date):
        try:
            return Birthday(date)
        except ValueError as error:
            print(self._name.value, ' : ', error)

    def find_phone(self, phone):  # пошук
        for el in self._phones:
            if str(el) == phone:
                return el

    def remove_phone(self, phone):  # Видалиня
        self._phones.remove(self.find_phone(phone))

    def edit_phone(self, phone, new_phone):  # редагуваня
        phone_obg = self.find_phone(phone)
        self._phones[self._phones.index(phone_obg)] = Phone(new_phone)

    def days_to_birthday(self):  # повертає кількість днів до наступного дня народженя
        current_date = datetime.now()
        next_birthday = datetime(current_date.year, self._birthday.value.month, self._birthday.value.day)
        if current_date > next_birthday:
            next_birthday = datetime(current_date.year + 1, self._birthday.value.month, self._birthday.value.day)
        days_left = (next_birthday - current_date).days

        print(f"До наступного дня народження залишилося {days_left} днів.")
        return days_left

    def __str__(self):
        return f"Contact name: {self._name.value}, phones: {'; '.join(p.value for p in self._phones)}"

    def set_birthdate(self, new_date):
        self._birthday = new_date

    @property
    def birthday(self):
        return f'date of birth {self._birthday}'

    @birthday.setter
    def birthday(self, data):
        self._birthday = self.__add_birthday(data)

    @property
    def name(self):
        return self._name.value

    @name.setter
    def name(self, new_name):
        self._name = Name(new_name)

    @property
    def phone(self):
        result = []
        for phon in self._phones:
            result.append(phon.value)
        return result

    @phone.setter
    def phone(self, phone):
        try:
            self._phones.append(Phone(phone))
        except ValueError as error:
            print(error)


class AddressBook(UserDict):  # Клас для зберігання та управління записами.

    def add_record(self, obg_record):  # додає запис до self.data
        self.data[str(obg_record.name)] = obg_record

    def find(self, name):  # знаходить запис за ім'ям.
        for key, value in self.data.items():
            if str(key) == name:
                return key, value

    def delete(self, name):
        for key in self.data.keys():
            if str(key) == name:
                self.data.pop(key)
                break

    def book_print(self):
        for key, value in self.data.items():
            print(f'{key} : {value}')

    def iterator(self, batch_size=1):
        return self.AddressBookIterator(self, batch_size)

    class AddressBookIterator:  # клас цо відповідае за ітерацію
        def __init__(self, address_book, batch_size):
            self.address_book = address_book
            self.__index = 0
            self.batch_size = batch_size

        def __iter__(self):
            return self

        def __next__(self):
            if self.__index >= len(self.address_book.data):
                raise StopIteration

            batch_end = min(self.__index + self.batch_size, len(self.address_book.data))
            batch = {
                key: self.address_book.data[key]
                for key in list(self.address_book.data.keys())[self.__index:batch_end]
            }
            self.__index += self.batch_size

            return batch
