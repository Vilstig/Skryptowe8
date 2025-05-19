import ipaddress
from http import HTTPStatus
from file_reader import log_first_100k

def is_valid_http_status(code):
    return code in {status.value for status in HTTPStatus}

def sort_log(log, index):
    try:
        return sorted(log, key=lambda x: x[index])
    except IndexError:
        print("Błąd: Podany indeks przekracza rozmiar krotek.")
        return log
    except TypeError:
        print("Błąd: Nieprawidłowy format danych – oczekiwano listy krotek.")
        return log


def test_sort_log():
    log_data = log_first_100k()
    sorted_log = sort_log(log_data, 3)

    for line in sorted_log:
        print(line)


def get_entries_by_addr(log, addr):
    try:
        addr_ip  = ipaddress.ip_address(addr)
        return [entry for entry in log if entry[2] == addr_ip]
    except ValueError:
        print(f"{addr} is not a valid IP address.")
        return []


def test_get_entries_by_addr():
    log_data = log_first_100k()
    filtered_log = get_entries_by_addr(log_data, '192.168.202.110')
    for entry in filtered_log:
        print(entry)

def get_entries_by_code(log, stat_code):
    if is_valid_http_status(stat_code):
        return [entry for entry in log if entry[9] == stat_code]

    print(f'{stat_code} is not a valid HTTP code.')
    return []

def test_get_entries_by_code():
    log_data = log_first_100k()
    filtered_log = get_entries_by_code(log_data, 200)
    for entry in filtered_log:
        print(entry)

def get_failed_reads(log, combine=False):
    l4 = [entry for entry in log if 99 < entry[9] < 1000 and int(entry[9]/100) == 4]
    l5 = [entry for entry in log if 99 < entry[9] < 1000 and int(entry[9]/100)==5]
    if combine:
        return l4+l5
    return l4, l5

def test_get_failed_reads():
    log_data = log_first_100k()
    result = get_failed_reads(log_data, True)
    if isinstance(result, tuple):
        for entry in result[0]:
            print(entry)
        for entry in result[1]:
            print(entry)
    else:
        for entry in result:
            print(entry)

def get_entries_by_extension(log, extension):
    return [entry for entry in log if entry[8].endswith(extension)]

def test_get_entries_by_extension():
    log_data = log_first_100k()
    filtered_log = get_entries_by_extension(log_data, '.jpg')
    for entry in filtered_log:
        print(entry)

if __name__ == '__main__':
    test_get_entries_by_extension()