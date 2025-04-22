import subprocess
from multiprocessing import Pool
import time

# Function to run fping on a chunk of IPs
def ping_chunk(chunk, progress_counter):
    result = subprocess.run(["fping", "-a", "-f", "-"], input="\n".join(chunk), capture_output=True, text=True)
    successful_pings = result.stdout.strip().splitlines()
    
    # Update progress and print out status every 10,000 pings
    progress_counter['count'] += len(successful_pings)
    if progress_counter['count'] % 100 == 0:
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Processed {progress_counter['count']} successful pings...")

    return successful_pings

# Function to chunk the hitlist into smaller lists for parallel processing
def chunk_ip_list(ip_list, chunk_size=100000):
    chunks = [ip_list[i:i + chunk_size] for i in range(0, len(ip_list), chunk_size)]
    return chunks

# Main function to process the hitlist
def main():
    # Load the hitlist of IP addresses
    with open("cs244/hitlist_old.txt", "r") as f:
        ip_addresses = f.read().splitlines()

    # Chunk the IP list into smaller parts (in memory, no files created)
    chunks = chunk_ip_list(ip_addresses)

    # Create a Pool of workers to process the chunks in parallel
    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Starting to process {len(ip_addresses)} IPs...")
    start_time = time.time()

    # Initialize a progress counter to track the number of successful pings
    progress_counter = {'count': 0}

    # Process the chunks in parallel with progress tracking
    with Pool(processes=32) as pool:
        results = pool.starmap(ping_chunk, [(chunk, progress_counter) for chunk in chunks])

    # Combine the results from all chunks
    successful_ips = [ip for result in results for ip in result]

    # Write successful IPs to a file
    with open("successful_pings.txt", "w") as f:
        f.write("\n".join(successful_ips))

    end_time = time.time()
    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Process completed. {len(successful_ips)} IPs are responsive.")
    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Total time taken: {end_time - start_time:.2f} seconds")

if __name__ == "__main__":
    main()



# PARALLEL TRY 3
# import subprocess
# import time
# import re
# import multiprocessing
# from tqdm import tqdm

# # This function will be executed by the worker processes
# def run_fping_on_chunk(chunk):
#     success_results = []
#     failed_results = []
#     for host in chunk:
#         success, rtt = ping_host(host)
#         timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
#         if success:
#             success_results.append((rtt, timestamp, host))
#         else:
#             failed_results.append((timestamp, host))
#     return success_results, failed_results

# def ping_host(host, count=1, timeout=55):
#     try:
#         output = subprocess.check_output(
#             ["fping", "-c", str(count), "-t", str(timeout), host],
#             stderr=subprocess.STDOUT,
#             universal_newlines=True
#         )

#         # Match the summary line: round-trip min/avg/max/stddev = ...
#         match = re.search(r'round-trip min/avg/max/stddev = ([\d.]+)/([\d.]+)/([\d.]+)/([\d.]+)', output)

#         if match:
#             avg_rtt = float(match.group(2))  # second value is avg
#             return True, avg_rtt
#         else:
#             return True, None  # packet received, but RTT not parsed

#     except subprocess.CalledProcessError:
#         return False, None

# # Load hostnames from file
# def load_hostnames(file_path):
#     with open(file_path, 'r') as f:
#         return [line.strip() for line in f if line.strip()]

# # Main function to execute the script
# def main():
#     print("[INFO] Loading hitlist...")
#     host_list = load_hostnames("cs244/hitlist_old.txt")
#     total_hosts = len(host_list)
#     print(f"[INFO] Total IPs loaded: {total_hosts}")

#     # Split the host list into chunks for parallel processing
#     chunk_size = 100  # Adjust the chunk size to balance workload and memory
#     chunks = [host_list[i:i + chunk_size] for i in range(0, total_hosts, chunk_size)]
#     print(f"[INFO] Split into {len(chunks)} chunks of size {chunk_size}")

#     # Set up the multiprocessing pool
#     num_workers = min(len(chunks), multiprocessing.cpu_count())  # Use the number of available CPU cores
#     print(f"[INFO] Using {num_workers} workers")

#     # Set up logging and progress bar
#     success_results = []
#     failed_results = []

#     with multiprocessing.Pool(num_workers) as pool:
#         for results in tqdm(pool.imap(run_fping_on_chunk, chunks), total=len(chunks)):
#             success, failed = results
#             success_results.extend(success)
#             failed_results.extend(failed)

#     # Sort successful pings by RTT
#     success_results.sort()

#     # Write the results to files
#     with open("ping_success_sorted.txt", "w") as success_log:
#         for rtt, timestamp, host in success_results:
#             success_log.write(f"{timestamp} {host} RTT={rtt}ms\n")

#     with open("ping_failure.txt", "w") as failure_log:
#         for timestamp, host in failed_results:
#             failure_log.write(f"{timestamp} {host} PING_FAILED\n")

#     print("[INFO] Finished processing.")

# if __name__ == "__main__":
#     main()




# PARALLEL TRY 2
# import subprocess
# import tempfile
# import os
# import time
# from multiprocessing import get_context

# # Constants
# CHUNK_SIZE = 100000
# MAX_PARALLEL = 16

# def log(msg):
#     timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
#     print(f"[{timestamp}] {msg}")

# def chunk_list(lst, n):
#     for i in range(0, len(lst), n):
#         yield lst[i:i + n]

# def run_fping_on_chunk(host_chunk_indexed):
#     idx, host_chunk = host_chunk_indexed
#     log(f"Started chunk {idx} with {len(host_chunk)} IPs")

#     with tempfile.NamedTemporaryFile(mode='w+', delete=False) as temp_file:
#         for ip in host_chunk:
#             temp_file.write(f"{ip}\n")
#         temp_file_path = temp_file.name

#     try:
#         output = subprocess.check_output(
#             ["fping", "-a", "-q", "-f", temp_file_path],
#             stderr=subprocess.STDOUT,
#             universal_newlines=True
#         )
#         os.remove(temp_file_path)
#         alive_ips = output.strip().split('\n')
#         log(f"Finished chunk {idx}: {len(alive_ips)} alive")
#         return alive_ips
#     except subprocess.CalledProcessError as e:
#         os.remove(temp_file_path)
#         output = e.output.strip().split('\n')
#         log(f"Finished chunk {idx} with error. Found {len(output)} possibly alive hosts")
#         return output

# def main():
#     log("Loading hitlist...")
#     with open("cs244/hitlist_old.txt", 'r') as f:
#         hosts = [line.strip() for line in f if line.strip()]

#     log(f"Total IPs loaded: {len(hosts)}")

#     chunks = list(enumerate(chunk_list(hosts, CHUNK_SIZE)))
#     log(f"Split into {len(chunks)} chunks of size {CHUNK_SIZE}")

#     with get_context("fork").Pool(processes=MAX_PARALLEL) as pool:
#         results = pool.map(run_fping_on_chunk, chunks)

#     all_alive_hosts = [ip for chunk_result in results for ip in chunk_result if ip]

#     log(f"Total responsive IPs: {len(all_alive_hosts)}")

#     with open("ping_success_fping.txt", "w") as f:
#         for ip in all_alive_hosts:
#             f.write(ip + "\n")

#     log("Finished writing output to ping_success_fping.txt")

# if __name__ == "__main__":
#     main()




# PARALLEL TRY 1
# import os
# import subprocess
# import tempfile
# import time
# from multiprocessing import Pool, cpu_count

# # CONFIGURABLE
# CHUNK_SIZE = 100_000   # Number of IPs per chunk
# MAX_PARALLEL = min(16, cpu_count())  # Number of parallel processes

# # Split IP list into chunks
# def split_into_chunks(ip_list, chunk_size):
#     for i in range(0, len(ip_list), chunk_size):
#         yield ip_list[i:i + chunk_size]

# # Run fping on a chunk of IPs
# def run_fping_on_chunk(args):
#     chunk, idx = args
#     timestamp = time.strftime("%Y-%m-%d %H:%M:%S")

#     with tempfile.NamedTemporaryFile(mode='w', delete=False) as temp_file:
#         for ip in chunk:
#             temp_file.write(f"{ip}\n")
#         temp_path = temp_file.name

#     try:
#         result = subprocess.run(
#             ["fping", "-q", "-a", "-f", temp_path],
#             stdout=subprocess.PIPE,
#             stderr=subprocess.PIPE,
#             universal_newlines=True
#         )

#         success_log = []
#         failure_log = []

#         stdout = result.stdout.strip().split("\n") if result.stdout else []
#         stderr = result.stderr.strip().split("\n") if result.stderr else []

#         alive_hosts = set(stdout)

#         for line in stderr:
#             parts = line.split()
#             if len(parts) >= 2:
#                 ip = parts[0]
#                 status = parts[1]
#                 if status == "alive":
#                     success_log.append(f"{timestamp} {ip}\n")
#                 else:
#                     failure_log.append(f"{timestamp} {ip} PING_FAILED\n")

#         return success_log, failure_log

#     finally:
#         os.remove(temp_path)

# # Load IPs from file
# def load_hostnames(file_path):
#     with open(file_path, 'r') as f:
#         return [line.strip() for line in f if line.strip()]

# # Main orchestration
# def main():
#     start_time = time.time()
#     all_ips = load_hostnames("cs244/hitlist_old.txt")
#     print(f"Loaded {len(all_ips):,} IPs")

#     chunks = list(enumerate(split_into_chunks(all_ips, CHUNK_SIZE)))
#     print(f"Split into {len(chunks)} chunks")

#     print(f"Running with {MAX_PARALLEL} parallel processes...")
#     with Pool(processes=MAX_PARALLEL) as pool:
#         results = pool.map(run_fping_on_chunk, chunks)

#     # Merge results
#     with open("fping_success.txt", "w") as f_succ, open("fping_failure.txt", "w") as f_fail:
#         for success_log, failure_log in results:
#             f_succ.writelines(success_log)
#             f_fail.writelines(failure_log)

#     elapsed = time.time() - start_time
#     print(f"✅ Done in {elapsed/60:.2f} minutes")

# if __name__ == "__main__":
#     main()




# NO PARALLELIZATION
# import subprocess
# import time
# import tempfile
# import os
# def load_hostnames(file_path):
#     with open(file_path, 'r') as f:
#         return [line.strip() for line in f if line.strip()]

# def run_fping(hosts):
#     # Write hosts to a temporary file
#     with tempfile.NamedTemporaryFile(mode='w', delete=False) as temp:
#         temp.writelines(f"{host}\n" for host in hosts)
#         temp_path = temp.name

#     try:
#         # Run fping on the list
#         result = subprocess.run(
#             ["fping", "-q", "-a", "-f", temp_path],
#             stdout=subprocess.PIPE,
#             stderr=subprocess.PIPE,
#             universal_newlines=True
#         )

#         # Alive hosts are printed to stdout
#         alive_hosts = set(result.stdout.strip().split("\n")) if result.stdout else set()

#         # All probed hosts are printed to stderr (with status)
#         status_lines = result.stderr.strip().split("\n")
#         timestamp = time.strftime("%Y-%m-%d %H:%M:%S")

#         success_log = []
#         failure_log = []

#         for line in status_lines:
#             parts = line.split()
#             if len(parts) >= 2:
#                 host = parts[0]
#                 status = parts[1]
#                 if status == "alive":
#                     success_log.append(f"{timestamp} {host}\n")
#                 elif status == "unreachable":
#                     failure_log.append(f"{timestamp} {host} PING_FAILED\n")

#         # Write logs
#         with open("fping_success.txt", "w") as f:
#             f.writelines(success_log)

#         with open("fping_failure.txt", "w") as f:
#             f.writelines(failure_log)

#         print(f"[✓] Scan complete: {len(success_log)} successful, {len(failure_log)} failed")

#     finally:
#         os.remove(temp_path)

# if __name__ == "__main__":
#     start = time.time()
#     host_list = load_hostnames("cs244/hitlist_old.txt")
#     run_fping(host_list)
#     print(f"Total time: {(time.time() - start)/60:.2f} minutes")
