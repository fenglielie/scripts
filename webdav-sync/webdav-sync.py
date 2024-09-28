import os
import http.client
import json
from urllib.parse import urlparse
import base64
import sys
import argparse


def load_config(config_file):
    """加载配置文件"""
    with open(config_file, "r") as f:
        return json.load(f)


def sync_with_webdav(config):
    """将指定后缀的文件同步到 WebDAV 服务器"""
    parsed_url = urlparse(config["webdav_url"])
    credentials = f"{config['username']}:{config['password']}"
    encoded_credentials = base64.b64encode(credentials.encode()).decode()
    files_to_upload = []

    for root, dirs, files in os.walk(config["local_folder"]):
        for file in files:
            if any(file.endswith(ext) for ext in config["include_extensions"]):
                local_path = os.path.join(root, file)
                remote_path = os.path.join(
                    parsed_url.path, os.path.relpath(local_path, config["local_folder"])
                ).replace("\\", "/")
                files_to_upload.append((local_path, remote_path))

    total_files = len(files_to_upload)
    success_count = 0
    failure_count = 0
    failure_details = []

    for local_path, remote_path in files_to_upload:
        with open(local_path, "rb") as f:
            conn = http.client.HTTPSConnection(parsed_url.netloc)
            headers = {
                "Authorization": f"Basic {encoded_credentials}",
                "User-Agent": "Python-WebDAV-Sync",
            }
            try:
                conn.request("PUT", remote_path, f.read(), headers)
                response = conn.getresponse()
                if response.status == 201:
                    success_count += 1
                else:
                    failure_count += 1
                    failure_details.append(
                        f"Failed to upload {local_path} to {remote_path}: {response.status} {response.reason}"
                    )
            except Exception as e:
                failure_count += 1
                failure_details.append(
                    f"Exception occurred while uploading {local_path}: {str(e)}"
                )
            finally:
                conn.close()

        progress = (success_count + failure_count) / total_files * 100
        sys.stdout.write(
            f"\rProgress: {progress:.2f}% ({success_count + failure_count}/{total_files})"
        )
        sys.stdout.flush()

    print("\nUpload completed.")
    print(
        f"Total files: {total_files}, Successful: {success_count}, Failed: {failure_count}"
    )

    if failure_details:
        print("\nFailure Details:")
        for detail in failure_details:
            print(detail)


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="Sync files to a WebDAV server.")
    parser.add_argument(
        "-c",
        "--config",
        type=str,
        default=os.path.expanduser("~/.config/py-webdav-sync/config.json"),
        help="Specify the configuration file (default: ~/.config/py-webdav-sync/config.json)",
    )

    args = parser.parse_args()
    config_file = args.config

    # 读取配置
    configs = load_config(config_file)

    # 获取当前执行目录的绝对路径
    current_path = os.path.abspath(os.getcwd())

    # 对比并同步
    matched = False
    for project_id, config in configs.items():
        if os.path.abspath(config["local_folder"]) == current_path:
            print(f"Matched configuration: {project_id}\nStarting synchronization...")
            sync_with_webdav(config)
            matched = True
            break

    if not matched:
        print("No matching configuration found.")


if __name__ == "__main__":
    main()
