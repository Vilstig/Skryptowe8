import ipaddress
import datetime


class HttpLog:
    def __init__(self, log_file):
        self.log_file = log_file
        self.entries = []
        self.events = []
        self._load_entries()


    def _load_entries(self):
        try:
            with open(self.log_file, 'r') as f:
                for line in f:
                    try:
                        entry = HttpLogEntry(line)
                        self.entries.append(entry)
                    except ValueError as e:
                        self.events.append(f"Skipping line with error: {e}")

        except FileNotFoundError:
            raise FileNotFoundError(f"File {self.log_file} not found.")


class HttpLogEntry:
    def __init__(self, line: str):
        parsed_line = line.strip().split('\t')

        try:
            ts = float(parsed_line[0])
            self.timestamp = datetime.datetime.fromtimestamp(ts)
            self.uid = parsed_line[1]
            self.id_orig_h = ipaddress.ip_address(parsed_line[2])
            self.id_orig_p = int(parsed_line[3])
            self.id_resp_h = ipaddress.ip_address(parsed_line[4])
            self.id_resp_p = int(parsed_line[5])
            self.method = parsed_line[7]
            self.host = ipaddress.ip_address(parsed_line[8])
            self.uri = parsed_line[9]
            self.request_body_len = int(parsed_line[12])
            self.response_body_len = int(parsed_line[13])
            self.stat_code = int(parsed_line[14])

        except (ValueError, IndexError) as e:
            raise ValueError(f"Invalid log line format: {e}")

    def __str__(self):
        return (f"[{self.timestamp}] UID: {self.uid} "
                f"{self.id_orig_h}:{self.id_orig_p} -> {self.id_resp_h}:{self.id_resp_p} "
                f"{self.method} {self.uri} "
                f"ReqLen={self.request_body_len} RespLen={self.response_body_len} "
                f"Status={self.stat_code}")

    def to_dict(self):
        return {
            'ts': self.timestamp,
            'uid': self.uid,
            'id_orig_h': str(self.id_orig_h),
            'id_orig_p': self.id_orig_p,
            'id_resp_h': str(self.id_resp_h),
            'id_resp_p': self.id_resp_p,
            'method': self.method,
            'host': str(self.host),
            'uri': self.uri,
            'request_body_len': self.request_body_len,
            'response_body_len': self.response_body_len,
            'stat_code': self.stat_code
        }

def main():

    log = HttpLog('http_first_100k.log')

    for entry in log.entries:
        print(entry)


if __name__ == '__main__':
    main()


