import sys
import argparse
import dns.resolver


def read_servers_from_file(file_path):
    servers = []
    try:
        with open(file_path, 'r') as file:
            for line in file:
                parts = line.strip().split()
                if len(parts) == 2:
                    servers.append((parts[0], parts[1]))
                else:
                    print(f"Skipping invalid line in servers.conf: {line}")
    except FileNotFoundError:
        print(f"Error: {file_path} not found.")
    return servers


def resolve_dns_record(hostname, dns_server, record_type):
    try:
        resolver = dns.resolver.Resolver(configure=False)
        resolver.nameservers = [dns_server]

        if record_type == "A":
            answer = resolver.resolve(hostname, 'A')
            return [r.address for r in answer]
        elif record_type == "NS":
            answer = resolver.resolve(hostname, 'NS')
            return [r.target.to_text() for r in answer]
        elif record_type == "CNAME":
            answer = resolver.resolve(hostname, 'CNAME')
            return [r.target.to_text() for r in answer]
        else:
            return "Invalid record type"
    except dns.exception.DNSException as e:
        return str(e)


def check_hostname(hostname, dns_servers, record_type):
    results = {}

    for ip_address, name in dns_servers:
        result = resolve_dns_record(hostname, ip_address, record_type)
        results[name] = result

    return results


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Check DNS records for a hostname.")
    parser.add_argument("hostname", help="Hostname to check")
    parser.add_argument("--record-type", choices=["A", "NS", "CNAME"], default="A",
                        help="Type of DNS record to resolve (A, NS, or CNAME)")
    args = parser.parse_args()

    dns_servers = read_servers_from_file("servers.conf")

    if not dns_servers:
        print("No valid DNS servers found in servers.conf. Exiting.")
        sys.exit(1)

    results = check_hostname(args.hostname, dns_servers, args.record_type)

    for name, result in results.items():
        if args.record_type == "A":
            print(f"DNS Server: {name} | IP Address: {', '.join(result)}")
        elif args.record_type == "NS":
            print(f"DNS Server: {name} | NS Records: {', '.join(result)}")
        elif args.record_type == "CNAME":
            print(f"DNS Server: {name} | CNAME Records: {', '.join(result)}")
