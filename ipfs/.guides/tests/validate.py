#!/usr/bin/env python3
import random
import string
import time


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def validate(code_path):
    try:
        import ipfs
    except ImportError:
        print("Could not import homework file 'ipfs.py'")
        return 0

    required_methods = ["pin_to_ipfs", "get_from_ipfs"]
    for m in required_methods:
        if m not in dir(ipfs):
            print("%s not defined" % m)
            return 0

    num_tests = 4
    num_passed = 0
    # total possible points is (num_tests * 2) + (num_tests // 2) because student pin is tested on %2 runs only
    max_pts = (num_tests * 2) + (num_tests // 2)
    for t in range(num_tests):
        write_d = {'name': [random.choice(string.ascii_uppercase) for _ in range(5)],
                   'description': [random.choice(string.ascii_uppercase) for _ in range(10)]}

        if t % 2 == 0:
            student_write = True
            try:
                print(f"\n{bcolors.UNDERLINE}Testing your 'pin_to_ipfs()' method:{bcolors.ENDC}")
                cid = ipfs.pin_to_ipfs(write_d)
                num_passed += 1
                print(f"\t{bcolors.OKGREEN}SUCCESS{bcolors.ENDC}: Your 'pin_to_ipfs()' method successfully completed\n")
                time.sleep(2)
            except Exception as e:
                print(f"\t{bcolors.FAIL}ERROR{bcolors.ENDC}: your 'pin_to_ipfs' method did not complete successfully\n{e}\n")
                continue
        else:
            student_write = False
            cid = "QmeSjSinHpPnmXmspMjwiXyN6zS4E9zccariGR3jxcaWtq/" + str(489)  # Get a Bored Ape
            write_d = {"image": "ipfs://QmdytAmQteo21xzcdVAayKbU5AKqVCLkuGn4VnTbTbDTfC",
                       "attributes": [{"trait_type": "Fur", "value": "Noise"},
                                      {"trait_type": "Background", "value": "Orange"},
                                      {"trait_type": "Mouth", "value": "Bored Unshaven"},
                                      {"trait_type": "Eyes", "value": "Bored"},
                                      {"trait_type": "Hat", "value": "Commie Hat"},
                                      {"trait_type": "Clothes", "value": "Tanktop"}]}

        if student_write:
            print(f"{bcolors.UNDERLINE}Testing 'get_from_ipfs()' for data pinned by your 'pin_to_ipfs()' method:{bcolors.ENDC}")
        else:
            print(f"{bcolors.UNDERLINE}Testing 'get_from_ipfs()' with data already existing on ipfs network:{bcolors.ENDC}")

        attempts = 2  # Try again if gateway timeout or other failure
        success = False
        while attempts > 0:
            attempts -= 1
            try:
                read_d = ipfs.get_from_ipfs(cid)
                success = True
            except Exception as e:
                if attempts > 0:
                    time.sleep(2)
                    continue
                print(f"{bcolors.FAIL}ERROR{bcolors.ENDC}: reading {cid} from ipfs\n{e}\n")

        if success:
            print(f"\tTesting data type:")
            if isinstance(read_d, dict):
                num_passed += 1
                print(f"\t{bcolors.OKGREEN}SUCCESS{bcolors.ENDC}: You returned the result in the correct type")
            else:
                print(f"\t\texpected type: <class 'dict'>")
                print(f"\t\tpinned type: {type(write_d)},\treturned type: {type(read_d)}")
                print(f"\t{bcolors.FAIL}ERROR{bcolors.ENDC}: get_from_ipfs should return a dict")


            print(f"\tTesting data values:")
            if read_d == write_d:
                num_passed += 1
                print(f"\t{bcolors.OKGREEN}SUCCESS{bcolors.ENDC}: You returned the correct result\n")
            else:
                print(f"\t\texpected value: {write_d}\n\t\treturned value: {read_d}")
                print(f"\t{bcolors.FAIL}ERROR{bcolors.ENDC}: You did not return the correct result\n")

    return int(100 * float(num_passed) / max_pts)


if __name__ == '__main__':
    final_score = validate("")
    print(f"\nScore = {final_score}%")
