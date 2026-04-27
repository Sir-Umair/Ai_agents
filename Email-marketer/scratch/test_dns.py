import dns.resolver
import sys

try:
    resolver = dns.resolver.Resolver(configure=False)
    resolver.nameservers = ['8.8.8.8', '8.8.4.4', '1.1.1.1']
    print(f"Testing resolution of cluster0.y6udkhq.mongodb.net using {resolver.nameservers}...")
    
    # Try resolving the SRV record
    result = resolver.resolve('_mongodb._tcp.cluster0.y6udkhq.mongodb.net', 'SRV')
    for val in result:
        print(f"SRV Record found: {val.target} port {val.port}")
    
    # Try resolving the name directly (Atlas hostnames often don't have A records directly on the SRV root)
    # result = resolver.resolve('cluster0.y6udkhq.mongodb.net', 'A')
    # print(f"A Record: {result[0]}")
    
    print("SUCCESS: Target resolved.")
except Exception as e:
    print(f"FAILURE: {type(e).__name__}: {e}")
