"""Network discovery for Ollama endpoints."""
import asyncio
import socket
from typing import List, Dict, Any
import ipaddress


async def discover_ollama_endpoints(
    subnet: str = "192.168.1.0/24",
    port: int = 11434,
    timeout: float = 2.0
) -> List[Dict[str, Any]]:
    """
    Discover Ollama endpoints on the local network.
    
    Args:
        subnet: Network subnet to scan (CIDR notation)
        port: Port to check (default 11434 for Ollama)
        timeout: Timeout for each connection attempt
    
    Returns:
        List of discovered endpoints with their models
    """
    discovered = []
    
    try:
        network = ipaddress.ip_network(subnet, strict=False)
        
        # Create tasks for all IPs in subnet
        tasks = []
        for ip in network.hosts():
            tasks.append(_check_ollama_endpoint(str(ip), port, timeout))
        
        # Run all checks concurrently
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter successful results
        for result in results:
            if isinstance(result, dict) and result:
                discovered.append(result)
    
    except Exception as e:
        print(f"Discovery error: {e}")
    
    return discovered


async def _check_ollama_endpoint(
    ip: str,
    port: int,
    timeout: float
) -> Dict[str, Any]:
    """Check if an IP has an Ollama endpoint and get available models."""
    try:
        import aiohttp
        
        endpoint = f"http://{ip}:{port}"
        
        async with aiohttp.ClientSession() as session:
            # Check if Ollama is running
            async with session.get(
                f"{endpoint}/api/tags",
                timeout=aiohttp.ClientTimeout(total=timeout)
            ) as resp:
                if resp.status != 200:
                    return {}
                
                data = await resp.json()
                models = data.get('models', [])
                
                if not models:
                    return {}
                
                # Get hostname if possible
                hostname = ip
                try:
                    hostname = socket.gethostbyaddr(ip)[0]
                except:
                    pass
                
                return {
                    "ip": ip,
                    "endpoint": endpoint,
                    "hostname": hostname,
                    "models": [m['name'] for m in models],
                    "port": port
                }
    
    except Exception:
        return {}


async def check_local_ollama() -> Dict[str, Any]:
    """Check for Ollama on localhost."""
    result = await _check_ollama_endpoint("127.0.0.1", 11434, 2.0)
    if result:
        result["hostname"] = "localhost"
    return result


async def discover_with_progress(
    subnet: str,
    progress_callback=None
) -> List[Dict[str, Any]]:
    """
    Discover endpoints with progress reporting.
    
    Args:
        subnet: Network to scan
        progress_callback: Function to call with (current, total) progress
    
    Returns:
        List of discovered endpoints
    """
    discovered = []
    
    try:
        network = ipaddress.ip_network(subnet, strict=False)
        ips = list(network.hosts())
        total = len(ips)
        
        # Check in batches to avoid overwhelming the network
        batch_size = 50
        for i in range(0, total, batch_size):
            batch = ips[i:i + batch_size]
            
            tasks = [_check_ollama_endpoint(str(ip), 11434, 1.0) for ip in batch]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            for result in results:
                if isinstance(result, dict) and result:
                    discovered.append(result)
            
            if progress_callback:
                progress_callback(min(i + batch_size, total), total)
    
    except Exception as e:
        print(f"Discovery error: {e}")
    
    return discovered


def get_local_subnet() -> str:
    """Attempt to determine the local subnet."""
    try:
        # Get local IP address
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        
        # Convert to /24 subnet
        parts = local_ip.split('.')
        subnet = f"{parts[0]}.{parts[1]}.{parts[2]}.0/24"
        return subnet
    
    except Exception:
        # Default to common private subnet
        return "192.168.1.0/24"
