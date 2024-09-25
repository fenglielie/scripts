#!/usr/bin/env python3

import os
import shutil
import json
import argparse
import time
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path


def setup_logging(log_file_path, max_bytes=5 * 1024 * 1024, backup_count=5):
    """
    设置日志系统，使用 RotatingFileHandler 进行日志轮转。

    :param log_file_path: 日志文件的路径。
    :param max_bytes: 单个日志文件的最大字节数（默认 5MB）。
    :param backup_count: 保留的备份日志文件数量（默认 5 个）。
    """
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    # 创建 RotatingFileHandler
    rotating_handler = RotatingFileHandler(
        log_file_path, maxBytes=max_bytes, backupCount=backup_count, encoding="utf-8"
    )

    # 创建日志格式
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    rotating_handler.setFormatter(formatter)

    # 添加处理器到日志记录器
    logger.addHandler(rotating_handler)

    # 添加 StreamHandler 将日志输出到控制台
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)


def normalize_path(path):
    """
    规范化路径，转换为绝对路径并统一使用 '/' 作为分隔符。

    :param path: 原始路径。
    :return: 规范化后的路径。
    """
    return str(Path(path).resolve()).replace("\\", "/")


def load_config(config_path):
    """
    加载 JSON 配置文件。

    :param config_path: 配置文件路径。
    :return: 配置内容。
    """
    with open(config_path, "r") as file:
        config = json.load(file)
    return config


def create_timestamped_folder(base_path):
    """
    在基路径下创建一个带时间戳的文件夹。

    :param base_path: 基路径。
    :return: 创建的时间戳文件夹路径。
    """
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    destination_path = os.path.join(base_path, timestamp)
    os.makedirs(destination_path, exist_ok=True)
    return destination_path


def get_existing_backups(base_path):
    """
    获取基路径下所有现有的备份文件夹，并按名称排序。

    :param base_path: 基路径。
    :return: 排序后的备份文件夹列表。
    """
    return sorted(
        [f for f in os.listdir(base_path) if os.path.isdir(os.path.join(base_path, f))]
    )


def manage_backup_rotation(base_path, max_backups):
    """
    管理备份轮转，如果备份数量超过最大值，则删除最早的备份。

    :param base_path: 基路径。
    :param max_backups: 最大备份数量。
    """
    existing_backups = get_existing_backups(base_path)
    if len(existing_backups) > max_backups:
        oldest_backup = os.path.join(base_path, existing_backups[0])
        shutil.rmtree(oldest_backup)
        logging.info(f"Deleted oldest backup: {normalize_path(oldest_backup)}")


def backup(source, destination):
    """
    执行备份操作，将源复制到目标。

    :param source: 源路径。
    :param destination: 目标路径。
    """
    source = normalize_path(source)
    destination = normalize_path(destination)

    if os.path.exists(source):
        try:
            if os.path.isdir(source):
                shutil.copytree(source, destination, dirs_exist_ok=True)
                logging.info(f"Backed up folder: {source} to {destination}")
            else:
                destination_folder = os.path.dirname(destination)
                os.makedirs(destination_folder, exist_ok=True)
                shutil.copy2(source, destination)
                logging.info(f"Backed up file: {source} to {destination}")
        except Exception as e:
            logging.error(f"Failed to back up {source} to {destination}. Error: {e}")
    else:
        logging.warning(f"Source not found: {source}")


def rollback(source, destination):
    """
    执行回滚操作，将目标复制回源。

    :param source: 源路径。
    :param destination: 目标路径。
    """
    source = normalize_path(source)
    destination = normalize_path(destination)

    if os.path.exists(destination):
        try:
            if os.path.isdir(destination):
                shutil.copytree(destination, source, dirs_exist_ok=True)
                logging.info(f"Rolled back folder: {destination} to {source}")
            else:
                os.makedirs(os.path.dirname(source), exist_ok=True)
                shutil.copy2(destination, source)
                logging.info(f"Rolled back file: {destination} to {source}")
        except Exception as e:
            logging.error(f"Failed to roll back {destination} to {source}. Error: {e}")
    else:
        logging.warning(f"Backup not found: {destination}")


def main():
    parser = argparse.ArgumentParser(
        description="Backup and rollback script with timestamped folders and log rotation"
    )
    parser.add_argument(
        "--config", required=True, help="Path to the configuration file"
    )
    parser.add_argument("--log", required=True, help="Path to the log file")
    parser.add_argument(
        "--rollback", action="store_true", help="Perform rollback instead of backup"
    )
    args = parser.parse_args()

    # 规范化配置文件路径
    config_path = normalize_path(args.config)

    # 确定日志文件路径
    log_file_path = normalize_path(args.log)


    # 设置日志系统，启用日志轮转
    setup_logging(log_file_path)

    logging.info(f"Configuration file: {config_path}")
    logging.info(f"Log file: {log_file_path}")

    try:
        config = load_config(config_path)
    except Exception as e:
        logging.error(f"Failed to load configuration file: {config_path}. Error: {e}")
        # print("Error: Failed to load configuration file. Check log for details.")
        return

    base_destination = normalize_path(config.get("destination", ""))
    if not base_destination:
        logging.error("'destination' not specified in configuration file.")
        # print("Error: 'destination' not specified in configuration file.")
        return

    max_backups = config.get("max_backups", 10)  # 默认最大备份数量为10
    if not isinstance(max_backups, int) or max_backups < 1:
        logging.error("'max_backups' must be an integer greater than 0.")
        # print("Invalid value for 'max_backups'. Must be an integer greater than 0.")
        return

    backup_paths = config.get("backup_paths", [])
    if not isinstance(backup_paths, list) or not backup_paths:
        logging.error("'backup_paths' must be a non-empty list in configuration file.")
        # print("Error: 'backup_paths' must be a non-empty list in configuration file.")
        return

    if args.rollback:
        logging.info("Starting rollback process")
        # 获取最近的备份路径
        existing_backups = get_existing_backups(base_destination)
        if not existing_backups:
            logging.warning("No backups available for rollback.")
            # print("Warning: No backups available for rollback.")
            return
        latest_backup = os.path.join(base_destination, existing_backups[-1])
        logging.info(f"Rolling back from: {normalize_path(latest_backup)}")

        # 执行回滚操作
        for path in backup_paths:
            backup_name = os.path.basename(path)
            backup_destination = os.path.join(latest_backup, backup_name)
            rollback(path, backup_destination)

    else:
        logging.info("Starting backup process")
        # 创建带时间戳的备份文件夹
        try:
            destination_path = create_timestamped_folder(base_destination)
            logging.info(f"Backing up to: {normalize_path(destination_path)}")
        except Exception as e:
            logging.error(
                f"Failed to create backup directory: {base_destination}. Error: {e}"
            )
            # print("Error: Failed to create backup directory. Check log for details.")
            return

        # 执行备份操作
        for path in backup_paths:
            backup_destination = os.path.join(destination_path, os.path.basename(path))
            backup(path, backup_destination)

        # 进行备份轮替管理
        try:
            manage_backup_rotation(base_destination, max_backups)
        except Exception as e:
            logging.error(f"Failed to manage backup rotation. Error: {e}")
            # print("Error: Failed to manage backup rotation. Check log for details.")

    logging.info("Operation completed")


if __name__ == "__main__":
    main()
