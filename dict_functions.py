from file_reader import log_first_100k


def entry_to_dict(log_entry):
    keys = ['ts', 'uid', 'id_orig_h', 'id_oirg_p', 'id_resp_h', 'id_resp_p', 'method', 'host', 'uri', 'stat_code']
    return dict(zip(keys, log_entry))

def log_to_dict(log):
    log_dict = {}

    for entry in log:
        entry_dict = entry_to_dict(entry)
        uid = entry_dict['uid']

        if uid not in log_dict:
            log_dict[uid] = []

        log_dict[uid].append(entry_dict)

    return log_dict

def print_dict_entry_dates(dict_log):
    ret_dict = {}
    for key in dict_log:
        dict_list = dict_log[key]
        for dict_entry in dict_list:
            host_ip = dict_entry['id_orig_h']
            num_2xx = 1 if 99<dict_entry['stat_code']<1000 and int(dict_entry['stat_code']/100)==2 else 0
            if host_ip not in ret_dict: #creating entry for ip that hasnt been encountered yet
                ret_dict[host_ip] = {'req_count':1, 'first_req':dict_entry['ts'], 'last_req':dict_entry['ts'], 'meth_dict':{dict_entry['method']: 1}, '2xx_count': num_2xx}
            else:
                ret_dict[host_ip]['req_count']+=1
                if dict_entry['ts'] < ret_dict[host_ip]['first_req']:
                    ret_dict[host_ip]['first_req'] = dict_entry['ts']
                elif dict_entry['ts'] > ret_dict[host_ip]['last_req']:
                    ret_dict[host_ip]['last_req'] = dict_entry['ts']
                ret_dict[host_ip]['meth_dict'][dict_entry['method']] = ret_dict[host_ip]['meth_dict'].get(dict_entry['method'], 0) + 1
                ret_dict[host_ip]['2xx_count'] += num_2xx

    for host in ret_dict:
        print(f"Host: {host}\nRequest count: {ret_dict[host]['req_count']}\nFirst request date: {ret_dict[host]['first_req']} \nLast request date: {ret_dict[host]['last_req']} "
              f"\nMethod percentages: ")
        for meth in ret_dict[host]['meth_dict']:
            print(f"{meth} - {round(ret_dict[host]['meth_dict'][meth]/ret_dict[host]['req_count']*100, 2)}%")
        print(f"2xx ratio: {round(ret_dict[host]['2xx_count']/ret_dict[host]['req_count'], 4)}\n")

        
def test_entry_to_dict():
    log = log_first_100k()
    log_entry_dict = entry_to_dict(log[7])
    print(log_entry_dict)

def test_log_to_dict():
    log = log_first_100k()
    log_dict = log_to_dict(log)
    for key, entries in log_dict.items():
        print(f"UID: {key}")
        for entry in entries:
            print(entry)

def test_print_dict_entry_dates():
    log = log_first_100k()
    log_dict = log_to_dict(log)
    print_dict_entry_dates(log_dict)

if __name__ == '__main__':
    #test_entry_to_dict()
    #test_log_to_dict()
    test_print_dict_entry_dates()