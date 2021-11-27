import os
import random as RD
import json


class Fore:
    LIGHTGREEN_EX = ''
    LIGHTBLUE_EX = ''
    GREEN = ''
    RED = ''
    YELLOW = ''
    CYAN = ''


class Style:
    RESET_ALL = ''


try:
    from colorama import Fore, Style
    pass
except:
    print("colorama import failed")


def clear_terminal():
    os.system('cls' if os.name == 'nt' else 'clear')
    return False


# Emulate Database table names
files = {'users': 'users', 'tickets': 'tickets'}


def file_operation(file_name, data=None):  # Emulate Database R/W operations
    # don't worry if you don't have the files for initial run
    try:
        if data:
            with open(f"{file_name}.json", 'w') as outfile:
                json.dump(data, outfile)
        else:
            with open(f"{file_name}.json", 'r') as openfile:
                json_object = json.load(openfile)
                return json_object
    except:
        return False


# Load records to memory and Emulate Database tables
users = file_operation(files['users'])
if not users:
    users = {}
tickets = file_operation(files['tickets'])
if not tickets:
    tickets = {}


username = ''  # Emulate redis cache for tockens


def pretty_print_statement(string, line='.', length=6, color=''):
    print(f"\n{color}{line*length}{string}{line*length}\n{Style.RESET_ALL}")


def register():
    user_name = input("enter username: ").strip()
    if not user_name:
        pretty_print_statement("Invalid Username!", color=Fore.RED)
        return False
    elif user_name in users:
        pretty_print_statement("Username Already Taken!", color=Fore.RED)
        return False
    password = input("enter password: ").strip()
    if not password:
        pretty_print_statement("Invalid Password!", color=Fore.RED)
        return False
    selected = input("Confirm details?(y/n): ").strip().lower()
    global username
    if selected == 'y':
        users[user_name] = password
        pretty_print_statement("Registered! Please Login",
                               color=Fore.LIGHTGREEN_EX)
        file_operation(files['users'], users)
        return True
    return False


def login():
    user_name = input("enter username: ").strip()
    password = input("enter password: ").strip()
    response = user_name in users and password == users[user_name]
    pretty_print_statement(
        "Logged in!", color=Fore.LIGHTGREEN_EX) if response else pretty_print_statement(
        "Login Failed Try again!", color=Fore.RED)
    if response:
        global username
        username = user_name
    return response


def ticket_query():
    date = input("Enter travel date  : ")
    from_location = input("enter from location: ")
    to_location = input("enter to location  : ")
    if date and from_location and to_location:
        return {'date': date, 'from_location': from_location,
                'to_location': to_location}
    pretty_print_statement("Empty Details Entered!", color=Fore.RED)
    return False


def generate_ticket():
    def rand_no(digits): return str(RD.random())[2:][:min(digits, 8)]
    ticket_no = rand_no(7)
    seat_no = rand_no(2)
    coach_no = rand_no(1)
    return{'ticket_no': ticket_no, 'seat_no': seat_no,
           'coach_no': coach_no}


def confirm_ticket(username, ticket_details):
    if users[username] == input("Enter your password to confirm: "):
        return ticket_details
    pretty_print_statement("Ticket Confirmation Failed!", color=Fore.RED)
    return False


def pretty_print_ticket(ticket_detils):
    string = '-'*25+'\n'
    for key in list(ticket_detils.keys()):
        spaces = max(14 - len(key), 1)
        string += f"{key}{' '*spaces}: {ticket_detils[key]}\n"
    string += '='*25
    print(f'{Fore.LIGHTBLUE_EX}{string}{Style.RESET_ALL}')


def save_ticket_and_display(username, ticket_details):
    if username not in tickets:
        tickets[username] = []
    tickets_list = tickets[username]
    tickets_list.append(ticket_details)
    file_operation(files['tickets'], tickets)
    pretty_print_statement("Your ticket is confirmed!",
                           color=Fore.LIGHTGREEN_EX)
    pretty_print_ticket(ticket_details)


def view_tickets():
    global username
    if username in tickets and len(tickets[username]):
        i = 1
        for ticket_detils in tickets[username]:
            print(f"{Fore.CYAN}SL no.: {str(i)}{Style.RESET_ALL}")
            pretty_print_ticket(ticket_detils)
            response = input(
                "--press any key to continue or q to quit--"
            ).strip().lower()
            i += 1
            if response == 'q':
                break
    else:
        pretty_print_statement("No History Available!",
                               color=Fore.LIGHTYELLOW_EX)
    pretty_print_statement("END", '-', 11, color=Fore.YELLOW)


def booking_flow():
    booking_details = ticket_query()
    if not booking_details:
        pretty_print_statement("Booking Failed!", color=Fore.RED)
        return False
    ticket_details = generate_ticket()
    global username
    ticket_details = {**booking_details, **ticket_details}
    confirmed = confirm_ticket(username, ticket_details)
    if not confirmed:
        pretty_print_statement("Booking Failed!", color=Fore.RED)
        return False
    save_ticket_and_display(username, ticket_details)
    return True


def log_out():
    selected = input("Confirm Logout?(y/n): ").lower()
    global username
    if selected == 'y':
        username = ''
        pretty_print_statement("Logged Out!", color=Fore.LIGHTYELLOW_EX)
        return True
    return False


def quit():
    pretty_print_statement("Quitting!", '*', 8, color=Fore.YELLOW)
    return True


states = {  # Emulate frontend using cli
    1: {
        'query':
        lambda: input(
            "Login or Register or Quit? (l/r/q/cls): ")
            .strip().lower(),
        'functions': {
            'l': {'f': login, 's': 2},
            'r': {'f': register, 's': 1},
            'q': {'f': quit, 's': 0},
            'cls': {'f': clear_terminal, 's': 1},
        }
    },
    2: {
        'query':
        lambda: input(
            "Book Ticket or View Tickets or Logout?(b/v/l/cls): ")
            .strip().lower(),
        'functions': {
            'b': {'f': booking_flow, 's': 2},
            'v': {'f': view_tickets, 's': 2},
            'l': {'f': log_out, 's': 1},
            'cls': {'f': clear_terminal, 's': 2},
        }
    },
}


def state_manager(state):
    state_obj = states[state]
    response = state_obj['query']()
    if response in state_obj['functions']:
        success = False
        success = state_obj['functions'][response]['f']()
        if success:
            state = state_obj['functions'][response]['s']
    return state


def main():
    pretty_print_statement(
        "STARTING APPLICATION(use cls to clear)", '*', 10, Fore.GREEN)
    state = 1
    while state:
        state = state_manager(state)


main()  # Execution starts here
