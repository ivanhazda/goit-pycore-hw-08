from collections import UserDict
from datetime import datetime, timedelta
import pickle




class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)

class Name(Field):
    def __init__(self, value):
        super().__init__(value)

class Phone(Field):
    def __init__(self, value):
        if not self.validate_phone(value):
            raise ValueError("Phone number can only consist of 10 digits.")
        super().__init__(value)

    def validate_phone(self, value):
        return len(value) == 10 and value.isdigit()

class Birthday(Field):
    def __init__(self, value):
        try:
            datetime.strptime(value, "%d.%m.%Y").date()
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")
        self.value = value




class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def add_phone(self, phone_number):
        self.phones.append(Phone(phone_number))

    def find_phone(self, phone_number):
      for phone in self.phones:
            if phone.value == phone_number:
                return phone
      return None

    def remove_phone(self, phone_number):
        phone = self.find_phone(phone_number)
        if phone:
            self.phones.remove(phone)
        else:
            raise ValueError(f"Phone number {phone_number} not found.")

    def edit_phone(self, phone_number_old, phone_number_new):
        phone = self.find_phone(phone_number_old)

        if not phone:
            raise ValueError(f"Phone number {phone_number_old} not found.")
        # Створюємо новий об'єкт Phone для валідації нового номера
        new_phone = Phone(phone_number_new)
        index = self.phones.index(phone)
        self.phones[index] = new_phone
        

    def add_birthday(self, birthday):
        self.birthday = Birthday(birthday)

    def __str__(self):
        phones = ", ".join(p.value for p in self.phones)
        birthday = self.birthday.value if self.birthday else "No birthday"
        return f"Name: {self.name.value}, Phones: {phones}, Birthday: {birthday}"

 
class AddressBook(UserDict):
    def add_record(self, record):
        self.data[record.name.value] = record

    def find(self, name):
        return self.data.get(name)

    def delete(self, name):
        if name in self.data:
            del self.data[name]
        else:
            raise ValueError(f"Record for {name} not found.")

    def birthdays(self):
        today = datetime.now().date()
        upcoming_birthdays = []

        for record in self.data.values():
            if record.birthday:
                birthday=datetime.strptime(record.birthday.value, "%d.%m.%Y").date()
                birthday_this_year = birthday.replace(year=today.year)

                if birthday_this_year < today:
                    birthday_this_year = birthday_this_year.replace(year=today.year + 1)

                days_until_birthday = (birthday_this_year - today).days
                print (birthday_this_year)
                if 0 <= days_until_birthday <= 7:
                    if birthday_this_year.weekday() == 5:  
                        greeting_date = birthday_this_year + timedelta(days=2)
                    elif birthday_this_year.weekday() == 6:  # неділя
                        greeting_date = birthday_this_year + timedelta(days=1)
                    else:
                        greeting_date = birthday_this_year

                    upcoming_birthdays.append({"Name": record.name.value, "birthday": greeting_date.strftime('%d.%m.%Y')})

        return f"Birthdays in next 7 days: {upcoming_birthdays}" if upcoming_birthdays else "No upcoming birthdays."

    def __str__(self):
      if not self.data:
            return "Адресна книга порожня."
      return "\n".join(str(record) for record in self.data.values())


def input_error(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValueError as e:
            return str(e)
        except KeyError:
            return "Contact not found."
        except IndexError:
            return "Invalid input. Please provide the correct number of arguments."
    return wrapper


@input_error
def parse_input(user_input):
    cmd, *args = user_input.split()
    cmd = cmd.strip().lower()
    return cmd, *args


@input_error
def add_contact(args, book: AddressBook):
    name, phone = args
    record = book.find(name)
    if record:
        record.add_phone(phone)
        return "Contact updated."
    else:
        record = Record(name)
        record.add_phone(phone)
        book.add_record(record)
        return "Contact added."

@input_error
def change_contact(args, book: AddressBook):
    name, old_phone, new_phone = args
    record = book.find(name)
    if record:
        record.edit_phone(old_phone, new_phone)
        return f"Contact updated {name}."
    return "Contact not found."

@input_error
def phone(args, book: AddressBook):
    name = args[0]
    record = book.find(name)
    if record:
        return "\n".join(phone.value for phone in record.phones)
    return "Contact not found."

@input_error
def add_birthday(args, book: AddressBook):
    name, birthday = args
    record = book.find(name)
    if record:
        record.add_birthday(birthday)
        return f"Birthday added for {name}: {birthday}."
    return "Contact not found."

@input_error
def show_birthday(args, book: AddressBook):
    name = args[0]
    record = book.find(name)
    if record and record.birthday:
        return record.birthday.value
    return "Birthday not set." if record else "Contact not found."

@input_error
def show_all_contacts(args, book: AddressBook):
    return str(book)

@input_error
def birthdays(args, book):
    return book.birthdays()
    
@input_error
def save_data(book, filename="addressbook.pkl"):
    with open(filename, "wb") as f:
        pickle.dump(book, f)

@input_error
def load_data(filename="addressbook.pkl"):
    try:
        with open(filename, "rb") as f:
            return pickle.load(f)
    except FileNotFoundError:
        return AddressBook()  # Повертаємо нову книгу, якщо файл не існує







def main():
    book = load_data()
 
    print("Welcome to the assistant bot!")
    while True:
        user_input = input("Enter a command: ")
        command, *args = parse_input(user_input)

        if command in ["close", "exit"]:
            save_data(book)
            print("Good bye!")
            break
        elif command == "hello":
            print("How can I help you?")
        elif command == "add":
            print(add_contact(args, book))
        elif command == "change":
            print(change_contact(args, book))
        elif command == "phone":
            print(phone(args, book))
        elif command == "all":
            print(show_all_contacts(args, book))
        # add-birthday - додаємо до контакту день народження в форматі DD.MM.YYYY
        elif command == "add-birthday":
            print(add_birthday(args, book))
        # show-birthday - показуємо день народження контакту
        elif command == "show-birthday":
            print(show_birthday(args, book))
        
        elif command == "birthdays":
            print(birthdays(args, book))
        else:
            print("Invalid command.")

if __name__ == "__main__":
    main()