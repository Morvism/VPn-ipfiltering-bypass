import paramiko
import requests
import os
import time
from typing import AnyStr, List, Pattern
import json
import subprocess
# اطلاعات مرتبط با API خود را وارد کنید
api_key = "api"  # API Token یا کلید API
email = "email"  # ایمیل مرتبط با حساب Cloudflare
zone_id = "zone_id"  # شناسه منطقه DNS مرتبط با دامنه
filtered_ips = [] 
def check_ping(ip):
    try:
        result = os.system(f"ping -c 1 {ip}")
        if result == 0:
            return True
        return False
    except:
        return False


def validateCloudflareCredentials(email, api_key, zone_id):
    # تابع اعتبارسنجی اعتبارها در کلادفلر
    """
    Args:
    email (str): The email address associated with the Cloudflare account.
    api_key (str): The API key associated with the Cloudflare account.
    zone_id (str): The ID of the DNS zone for which to validate the credentials.

    Returns:
    bool: True if the credentials are valid, False otherwise.
    """

    headers = {
        "X-Auth-Email": email,
        "X-Auth-Key": api_key,
        "Content-Type": "application/json"
    }
    url = f"https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records"
    response = requests.get(url, headers=headers)
    return response.status_code == 200

def getCloudflareExistingRecords(email, api_key, zone_id, subdomain):
        """
    Args:
    email (str): The email address associated with the Cloudflare account.
    api_key (str): The API key associated with the Cloudflare account.
    zone_id (str): The ID of the DNS zone for which to get the existing records.
    subdomain (str): The subdomain for which to get the existing records.

    Returns:
    list: A list of existing DNS records for the specified subdomain in the specified Cloudflare DNS zone.
    """

        headers = {
            "X-Auth-Email": email,
            "X-Auth-Key": api_key,
            "Content-Type": "application/json"
             }
        url = f"https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records?type=A&name={subdomain}"

        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return json.loads(response.text)["result"]

    # تابع دریافت رکوردهای موجود در کلادفلر
    

def deleteCloudflareExistingRecord(email: str, api_key: str, zone_id: str, record_id: str) -> None:
    # تابع حذف رکورد در کلادفلر
        """
    Args:
        email (str): Cloudflare account email address.
        api_key (str): Cloudflare API key.
        zone_id (str): ID of the DNS zone where the record belongs.
        record_id (str): ID of the DNS record to be deleted.

    Returns:
        None
    """

        headers = {
            "X-Auth-Email": email,
            "X-Auth-Key": api_key,
            "Content-Type": "application/json"
         }
        url = f"https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records/{record_id}"
        response = requests.delete(url, headers=headers)
        response.raise_for_status()


# Function to add a new DNS record in Cloudflare.

def addNewCloudflareRecord(email: str, api_key: str, zone_id: str, subdomain: str, ip: str) -> None:
    # تابع افزودن رکورد جدید در کلادفلر
       """
    Args:
        email (str): Cloudflare account email address.
        api_key (str): Cloudflare API key.
        zone_id (str): ID of the DNS zone where the record should be added.
        subdomain (str): Name of the subdomain to be added.
        ip (str): IP address to be associated with the subdomain.

    Returns:
        None
    """

       headers = {
           "X-Auth-Email": email,
           "X-Auth-Key": api_key,
           "Content-Type": "application/json"
          }

       url = f"https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records"
       data = {
        "type": "A",
        "name": subdomain,
        "content": ip,
        "ttl": 3600,
        "proxied": False
    }
       response = requests.post(url, headers=headers, json=data)
       response.raise_for_status()


def processRegex(cidr: str, include_reg: Pattern[AnyStr], exclude_reg: Pattern[AnyStr]) -> List[AnyStr]:
      """
    Args:
        cidr (str): A CIDR block of Cloudflare Network to be converted to IP addresses.
        include_reg (Pattern[AnyStr]): A Regex Pattern to include IPs
        exclude_reg (Pattern[AnyStr]): A Regex Pattern to exclude IPs

    Returns:
        List[AnyStr]: A list of IPs converted from cidr
    """
      cidr = cidr.strip()
      if cidr:
        print(f"Processing {cidr}...      \r", end='')
        if include_reg and not include_reg.match(cidr):
            return []
        if exclude_reg and exclude_reg.match(cidr):
            return []
        return processCIDR(cidr)


    # تابع پردازش Regex برای CIDR
def main():
    ip_list = ["ip1","ip2" , "and more ip"]  # لیست آی‌پی‌های مورد نظر خود را ویرایش کنید
    subdomain = "sub.domain.com"  # دامنه ساب دامین خود را ویرایش کنید

    # لیست آی‌پی‌های فیلتر شده

   
    while True:
        for ip in ip_list:
            if ip not in filtered_ips:
                print(f"Checking IP: {ip}")

                ping_result = check_ping(ip)
                ssh_connected = False
                
                if ping_result:
                    print(f"IP {ip} is pingable.")
                    
                    try:
                        ssh_client = paramiko.SSHClient()
                        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                        ssh_client.connect(ip, port=28, username="root", password="utUa9i3dNuqi4MXAbVjP")
                        
                        print(f"SSH connection to {ip} is successful.")
                        ssh_connected = True
                        
                        # اجرای دستورات SSH
                        stdin, stdout, stderr = ssh_client.exec_command("echo Hello, World!")
                        print(stdout.read().decode())
                        
                        # اجرای تابع validateCloudflareCredentials برای بررسی اعتبارها
                        if validateCloudflareCredentials(email, api_key, zone_id):
                            print("Cloudflare credentials are valid.")
                            
                            # دریافت رکوردهای موجود در کلادفلر
                            existing_records = getCloudflareExistingRecords(email, api_key, zone_id, subdomain)
                            print("Existing Cloudflare DNS records:", existing_records)
                            
                            for record in existing_records:
                                 if record["name"] == "sub.domain.com":
                                     record_id = record["id"]
                                     
                                     
                                 
                            # اضافه کردن رکورد جدید به Cloudflare
                            
                            for record in existing_records:
                                 if record["content"] not in filtered_ips:
                                    print(f"Deleting DNS record for IP: {record['content']}")
                                    deleteCloudflareExistingRecord(email, api_key, zone_id, record["id"])
                                    print(f"DNS record for IP {record['content']} deleted from Cloudflare.")
                            addNewCloudflareRecord(email, api_key, zone_id, subdomain, ip)
                            print("New DNS record added to Cloudflare.")
                            
                            filtered_ips.append(ip)  # افزودن به لیست آی‌پی‌های فیلتر شده
                        else:
                            print("Cloudflare credentials are not valid.")
                        
                    except paramiko.AuthenticationException:
                        print(f"Authentication failed for {ip}")
                    except paramiko.SSHException as e:
                        print(f"SSH connection error for {ip}: {e}")
                    finally:
                        if ssh_connected:
                            ssh_client.close()
                else:
                    print(f"IP {ip} is not reachable.")
                    filtered_ips.append(ip)  # افزودن به لیست آی‌پی‌های فیلتر شده تا دیگر استفاده نشود

        time.sleep(5)

if __name__ == "__main__":
    main()