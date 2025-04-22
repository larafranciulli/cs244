import subprocess
import time
import re

def load_hostnames(file_path):
    with open(file_path, 'r') as f:
        return [line.strip() for line in f if line.strip()]

# def ping_host(host, count=1, timeout=1):
#     try:
#         output = subprocess.check_output(
#             ["ping", "-c", str(count), "-W", str(timeout), host],
#             stderr=subprocess.STDOUT,
#             universal_newlines=True
#         )
#         match = re.search(r'time=(\d+\.\d+)', output)
#         rtt = float(match.group(1)) if match else None
#         return True, rtt
#     except subprocess.CalledProcessError:
#         return False, None

# def ping_host(host, count=1, timeout=1):
#     try:
#         output = subprocess.check_output(
#             ["ping", "-c", str(count), "-W", str(timeout), host],
#             stderr=subprocess.STDOUT,
#             universal_newlines=True
#         )

#         # Print for debug
#         print(f"--- Raw output from {host} ---\n{output}")

#         # Match `time=XX.XXX ms` in any line
#         match = re.search(r'time=([\d.]+)\s*ms', output)
#         rtt = float(match.group(1)) if match else None
#         return True, rtt

#     except subprocess.CalledProcessError as e:
#         print(f"[!] Ping failed for {host}. Output:\n{e.output}")
#         return False, None

def ping_host(host, count=1, timeout=1):
    try:
        output = subprocess.check_output(
            ["ping", "-c", str(count), "-W", str(timeout), host],
            stderr=subprocess.STDOUT,
            universal_newlines=True
        )

        # Debug output if you want to verify
        # print(f"--- Raw output from {host} ---\n{output}")

        # Match the summary line: round-trip min/avg/max/stddev = ...
        match = re.search(r'round-trip min/avg/max/stddev = ([\d.]+)/([\d.]+)/([\d.]+)/([\d.]+)', output)

        if match:
            avg_rtt = float(match.group(2))  # second value is avg
            return True, avg_rtt
        else:
            return True, None  # packet received, but RTT not parsed

    except subprocess.CalledProcessError as e:
        print(f"[!] Ping failed for {host}. Output:\n{e.output}")
        return False, None


def ping_and_sort(hosts):
    success_results = []
    failed_results = []

    for host in hosts:
        success, rtt = ping_host(host)
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        if success:
            print(f"[+] {host} RTT={rtt}ms")
            success_results.append((rtt, timestamp, host))
        else:
            print(f"[-] {host} PING_FAILED")
            failed_results.append((timestamp, host))

        time.sleep(0.2)  # optional small delay

    # Sort successful pings by RTT (ascending)
    success_results.sort()

    # Write logs
    with open("ping_success_sorted.txt", "w") as success_log:
        for rtt, timestamp, host in success_results:
            success_log.write(f"{timestamp} {host} RTT={rtt}ms\n")

    with open("ping_failure.txt", "w") as failure_log:
        for timestamp, host in failed_results:
            failure_log.write(f"{timestamp} {host} PING_FAILED\n")

if __name__ == "__main__":
    host_list = load_hostnames("hitlist.txt")
    ping_and_sort(host_list)
