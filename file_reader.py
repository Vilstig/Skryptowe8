import datetime
import ipaddress
import sys
from sys import dont_write_bytecode


def parse_log_line(line):
    parsed_line = line.strip().split('\t')

    try:
        ts = float(parsed_line[0])
        uid = parsed_line[1]
        id_orig_h = ipaddress.ip_address(parsed_line[2])
        id_orig_p = int(parsed_line[3])
        id_resp_h = ipaddress.ip_address(parsed_line[4])
        id_resp_p = int(parsed_line[5])
        method = parsed_line[7]
        host = ipaddress.ip_address(parsed_line[8])
        uri = parsed_line[9]
        stat_code = int(parsed_line[14])

        timestamp = datetime.datetime.fromtimestamp(ts)

        return timestamp, uid, id_orig_h, id_orig_p, id_resp_h,id_resp_p, method, host, uri, stat_code

    except ValueError:
        return None


def read_log(stream):
    log_entries = []

    for line in stream:
        line = line.strip()
        if line:
            parsed_entry = parse_log_line(line)
            if parsed_entry:
                log_entries.append(parsed_entry)

    return log_entries


def log_first_100k():
    with open('http_first_100k.log', 'r') as log_file:
        return read_log(log_file)

def main():
    log = log_first_100k()

    for line in log:
        print(line)


if __name__ == '__main__':
    main()