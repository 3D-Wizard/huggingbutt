import os
import zipfile
from pathlib import Path
import pandas as pd
from tensorboard.backend.event_processing import event_accumulator
from huggingbutt import settings
from huggingbutt.logger_util import get_logger


logger = get_logger()


def get_access_token():
    return os.environ.get("AGENTHUB_ACCESS_TOKEN")


def set_access_token(token):
    os.environ["AGENTHUB_ACCESS_TOKEN"] = token


def check_path(path):
    return os.path.exists(path)


def file_exists(path):
    if not os.path.exists(path):
        raise FileNotFoundError(f"{path} not found.")
    return path


def make_dir(path):
    if not check_path(path):
        os.makedirs(path)


def check_token(token):
    if token is None or token == "":
        return False
    return True


def safe_file_path(path):
    """
    Make sure the parent directory of the file already exists, if not, create it.
    :param path:
    :return:
    """
    if os.path.exists(path):
        raise FileExistsError("Target File is exists")
    parent_path = os.path.dirname(path)
    Path(parent_path).mkdir(parents=True, exist_ok=True)
    return path


def env_download_dest_path(user_name: str, env_name: str, version: str):
    """
    Return the local absolute path of the env to download
    :param user_name:
    :param env_name:
    :param version:
    :return:
    """
    return os.path.join(settings.real_cache_path, 'zip', f"{user_name}@{env_name}@{version}.zip")


def succ_env_path(user_name, env_name, version):
    return os.path.join(settings.downloaded_env_path, f"{user_name}@{env_name}@{version}")


def touch_succ_env(user_name, env_name, version):
    success_path = succ_env_path(user_name, env_name, version)
    if not os.path.exists(success_path):
        Path(success_path).touch()
    else:
        raise FileExistsError("File is exists.")


def agent_download_dest_path(user_name: str, agent_name: str, version: str, env_user_name: str, env_name: str):
    """
    Return the local absolute path of the agent to download
    :param user_name:
    :param agent_name:
    :param version:
    :return:
    """
    desc_files = os.path.join(settings.real_cache_path, 'zip', f"{user_name}@{agent_name}@{version}@{env_user_name}@{env_name}.zip")


def local_env_path(user_name, env_name, version):
    return os.path.join(settings.env_path, user_name, env_name, version)




def extract(zip_path, dest_path):
    with zipfile.ZipFile(zip_path, "r") as zip:
        zip.extractall(dest_path)


def extract_env(user_name, env_name, version):
    zip_file = env_download_dest_path(user_name, env_name, version)
    dest_path = local_env_path(user_name, env_name, version)
    extract(zip_file, dest_path)



def extract_tb_log(path: str) -> pd.DataFrame:
    """
    Extract data from tensorboard log files for upload to the server.
    :param path:
    :return:
    """
    if not os.path.isabs(path):
        path = os.path.abspath(path)

    event_file = ''

    for root, dirs, files in os.walk(path):
        for file in files:
            if file.find('tfevents'):
                event_file = os.path.join(root, file)
                break

    if not event_file:
        raise RuntimeError("Not found tensorboard events log file.")

    # load the event log file
    ea = event_accumulator.EventAccumulator(event_file)
    ea.Reload()

    # get all usable matrices
    metrics = ea.Tags().get('scalars')
    if len(metrics) < 1:
        raise Exception("Not found any metrics.")

    data = {}
    # save the step column value
    steps_col = []

    #
    max_length = -1
    for m in metrics:
        values = []
        temp_steps = []
        for d in ea.Scalars(m):
            values.append(d.value)
            temp_steps.append(d.step)

        if len(values) > max_length:
            max_length = len(values)
            # steps_cols will always save the steps with the max length variable.
            steps_col = temp_steps

        data[m.split('/')[-1]] = values

    # Align variable lengths
    for k, v in data.items():
        if len(v) < max_length:
            v.insert(0, 0)

    df = pd.DataFrame(data)
    df.insert(0, 'steps', steps_col)
    return df
