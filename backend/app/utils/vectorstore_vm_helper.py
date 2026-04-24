import os
import paramiko
from dotenv import load_dotenv
from core.config import settings

load_dotenv()

VM_USER = "xr23"
VM_HOST = "10.112.145.130"
VM_PASSWORD = os.getenv("VM_PASSWORD")

VM_BASE_PATH = "/home/xr23/Projects/pipecat-examples/whatsapp/vectorstore/chroma"


def extract_chatbot_id(db_path: str) -> str:
    if "chatbot_" not in db_path:
        raise ValueError(f"Invalid vector_db_path: {db_path}")

    return f"chatbot_{db_path.split('chatbot_')[-1].split('/')[0]}"


def deploy_vectorstore_to_vm(local_path: str, db_path: str):
    """
    Windows-compatible VM deployment using Paramiko (SSH with password)
    """

    if not VM_PASSWORD:
        raise ValueError("VM_PASSWORD not set in .env")

    folder_name = extract_chatbot_id(db_path)
    remote_path = f"{VM_BASE_PATH}/{folder_name}"

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    ssh.connect(
        hostname=VM_HOST,
        username=VM_USER,
        password=VM_PASSWORD
    )
    stdin, stdout, stderr = ssh.exec_command(f"mkdir -p {remote_path}")
    stdout.channel.recv_exit_status()
    sftp = ssh.open_sftp()

    for root, _, files in os.walk(local_path):
        for file in files:
            local_file = os.path.join(root, file)

            relative_path = os.path.relpath(local_file, local_path)
            remote_file = f"{remote_path}/{relative_path}"

            remote_dir = os.path.dirname(remote_file)

            try:
                sftp.stat(remote_dir)
            except:
                ssh.exec_command(f"mkdir -p {remote_dir}")

            sftp.put(local_file, remote_file)

    sftp.close()
    ssh.close()