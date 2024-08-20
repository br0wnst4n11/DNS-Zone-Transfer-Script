#!/usr/bin/env python3

import sys
import dns.resolver
import dns.reversename
import dns.zone
import dns.exception
import dns.query

TIMEOUT = 15.0

def getnameservers(fqdn):
    try:
        answers = dns.resolver.resolve(fqdn, 'NS')
        return [ns.to_text() for ns in answers]
    except dns.exception.DNSException as e:
        print(f"Error retrieving nameservers for {fqdn}: {e}")
        return []

def resolve_nameserver_to_ip(nameserver):
    try:
        answers = dns.resolver.resolve(nameserver, 'A')
        return answers[0].to_text()  # Return the first IP address found
    except dns.exception.DNSException as e:
        print(f"Error resolving nameserver {nameserver} to IP: {e}")
        return None

def perform_axfr(domain, nameserver):
    nameserver_ip = resolve_nameserver_to_ip(nameserver)
    if not nameserver_ip:
        return None

    try:
        transfer = dns.query.xfr(nameserver_ip, domain, lifetime=TIMEOUT)
        zone = dns.zone.from_xfr(transfer)
        return [zone[node].to_text(node) for node in zone.nodes.keys()]
    except dns.exception.DNSException as e:
        print(f"Error performing AXFR from {nameserver} ({nameserver_ip}) for {domain}: {e}")
        return None

def main():
    if len(sys.argv) != 2:
        print("Usage: ./DNS_Zone_Transfer.py <domain>")
        sys.exit(1)

    domain = sys.argv[1]
    nameservers = get_nameservers(domain)

    if not nameservers:
        print(f"No nameservers found for {domain}. Exiting.")
        sys.exit(1)

    for ns in nameservers:
        print(f"Trying AXFR from {ns}...")
        records = perform_axfr(domain, ns)
        if records:
            filename = f'{domain}{ns}axfr.txt'
            with open(filename, 'w') as f:
                f.write('\n'.join(records))
            print(f"AXFR successful from {ns}. Records saved in {filename}.")
        else:
            print(f"AXFR failed from {ns}.")

if name == '_main':
    main()
