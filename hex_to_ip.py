def hex_to_ip(hex_str):
    """Convert 8-char hex string like '01000000' to IP '1.0.0.0'"""
    ip_int = int(hex_str, 16)
    return ".".join(str((ip_int >> (8 * i)) & 0xFF) for i in reversed(range(4)))

def generate_hitlist(fsdb_path, output_path):
    with open(fsdb_path) as f_in, open(output_path, 'w') as f_out:
        for line in f_in:
            if line.startswith("#") or not line.strip():
                continue
            block, octets = line.strip().split()
            if octets == "-":
                continue
            base_ip = hex_to_ip(block)
            prefix = ".".join(base_ip.split('.')[:3])
            for octet in octets.split(','):
                ip = f"{prefix}.{int(octet, 16)}"
                f_out.write(ip + "\n")

# Use this to generate the file
# generate_hitlist("internet_address_verfploeter_hitlist_it99w-20220528.fsdb", "hitlist_old.txt")

generate_hitlist("cs244/internet_address_verfploeter_hitlist_it110w-20241211.fsdb", "hitlist_new.txt")


