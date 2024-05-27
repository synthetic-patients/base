###################################################################################
# ALEX'S UTILITIES
#
# alternatively
# url = "https://alx.gd/util"
# with httpimport.remote_repo(url):
#   import util
#
# poetry add pandas tabulate rich

import json
import os
import shlex
import struct
import platform
import subprocess
import tabulate
from IPython.display import clear_output
import rich
import datetime
import time
import random
import string
import pandas as pd
import logging
import importlib
from uuid import uuid4

from IPython import embed

import numpy as np
from pathlib import Path
import inspect
import sys

from rich import console

console = console.Console()


# allow saving / uploading of chart to plotly
# import chart_studio.plotly as py
# # import plotly.figure_factory as ff
# # import chart_studio.plotly as pfig
#
#
# def upload_fig(fig, filename):
#     plotly_api_key = PLOTLY_API_KEY
#     plotly_username = 'alexgoodell'
#     from chart_studio.tools import set_credentials_file
#     # Plotly Chart Studio authentication
#     set_credentials_file(
#         username=plotly_username,
#         api_key=plotly_api_key
#     )
#     chart_url = py.plot(fig,filename=filename,auto_open=False,fileopt='overwrite',sharing='public')
#     print(f"View this figure on [Plotly]({chart_url})")
#     return chart_url

# def debug_here():
#     frame = inspect.currentframe()
#     try:
#         frame = frame.f_back
#         embed()
#     finally:
#         del frame


def find_root_from_readme():
    # Attempt to find README.md in the current directory and up two levels
    max_levels_up = 2
    current_dir = os.path.abspath(os.curdir)

    for _ in range(max_levels_up + 1):
        # Construct the path to where README.md might be
        readme_path = os.path.join(current_dir, "README.md")

        # Check if README.md exists at this path
        if os.path.isfile(readme_path):
            # Return the absolute path if found
            return os.path.dirname(os.path.abspath(readme_path))

        # Move up one directory level
        current_dir = os.path.dirname(current_dir)

    # Return None if README.md was not found
    return None


ROOT_DIR = find_root_from_readme()
PAPER_DIR = os.path.join(ROOT_DIR, 'manuscript')
FIG_DIR = os.path.join(PAPER_DIR, 'figures')
AUDIO_DIR = os.path.join(ROOT_DIR, 'audio_files')

pd.set_option('display.max_colwidth', 70)


def configure_logging():
    filename = f"{ROOT_DIR}/logs/log.txt"
    if not os.path.exists(filename):
        os.makedirs(os.path.dirname(filename), exist_ok=True)
    logging.basicConfig(filename=filename,
                        filemode='w',
                        format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                        datefmt='%Y-%m-%d %H:%M',
                        level=logging.DEBUG)
    return filename


def get_root_dir():
    # assumes in the root/utilities folder
    return os.path.dirname(os.path.abspath("../README.md"))


def get_fig_dir():
    return get_root_dir() + "/manuscript/figures"


def reload():
    importlib.reload(util)


def generate_hash():
    return str(uuid4())

def generate_random_string():
    return ''.join(random.choice(string.ascii_lowercase) for _ in range(2)) + ''.join(
        random.choice(string.digits) for _ in range(2)) + ''.join(
        random.choice(string.ascii_lowercase) for _ in range(2)) + ''.join(
        random.choice(string.digits) for _ in range(2)) + ''.join(
        random.choice(string.ascii_lowercase) for _ in range(2))


def wait_rand():
    wait_time = random.randint(1, 3)
    time.sleep(wait_time)


def log_and_print(text):
    logging.info(text)
    print(text)


def log(text):
    logging.info(text)


def get_timestamp():
    timestamp = '{:%Y-%m-%d-T-%H-%M-%S}'.format(datetime.datetime.now())
    return timestamp


def printl(text):
    print(text, end="")


def cprint(text):
    clear_output(wait=True)
    print(text, flush=True)


def log_and_rich_print(text):
    logging.info(text)
    rich.print(text, flush=True)


def rprint(text):
    rich.print(text, flush=True)


def lp(text):
    log_and_rich_print(text)



def start_log_task(text):
    rich.print(f"[yellow] ◕ {text} [/yellow]", flush=True, end="...")
    logging.info(text)


def log_task(text):
    rich.print(f"[yellow] ⦿ {text} [/yellow]", flush=True)
    logging.info(text)


def end_log_task():
    rich.print(f"[yellow bold] Done [/yellow bold]", flush=True)
    logging.info("Done")

def log_mini_task(text, text2=None):
    if text2:
        text = text + "..." + str(text2)
    console.log(f" ─── {text} ", style="italic")
    logging.info(text)



def clear():
    os.system('cls' if os.name == 'nt' else 'clear')


def tab_cols(df, cns):
    for cn in cns:
        print("\n\n{}".format(titlecase(cn)))
        print(tabulate.tabulate(pd.DataFrame(df[cn].value_counts()), tablefmt="pipe", headers=['Name', 'Count']))


def tab(df, tbformat="heavy_grid"):
    print(tabulate.tabulate(df, headers='keys', tablefmt=tbformat, showindex=False))


def header(m):
    length = get_terminal_size()[0]
    print(colored(m, 'yellow'))
    print(colored('▒' * length, 'white'))


def alert(m, error_code):
    text_color = ['green', 'yellow', 'red', 'white'][error_code]
    length = get_terminal_size()[0]
    print(colored('\n   > ' + m, text_color))


def hr():
    length = get_terminal_size()[0]
    print(colored('-' * length, 'white'))


def logo():
    logo = '''
        ▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁
        ▏                                                                            ▕
        ▏                                                                            ▕
        ▏  ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓░░░░░░░░░░░░░░░░░░░░░░  ▕
        ▏  ▓▓▓▓              ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓░░░░░░░░░░░░░░░░░░░  ▕
        ▏  ▓▓▓▓  [bold]SYNTHETIC[/bold]   ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓░░░░░░░░░░░░░░  ▕
        ▏  ▓▓▓▓  [yellow bold]PATIENT[/yellow bold]     ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▒▒▒▒▒▓▓▒▒▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓░░░░░░░░░░  ▕
        ▏  ▓▓▓▓  [yellow]PROJECT[/yellow]     ▓▓▓▓▓▓▓▓▒░▒▒░░▒▒▒░▒▒▒░▒▒▒▒▒▒▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓░░░░░  ▕
        ▏  ▓▓▓▓              ▓▓▓▓▓▒░▒░░░░░░░░░░░░░░░░░▒▒▒▒▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓░░░  ▕
        ▏  ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▒▒░▒▒░░░░░░░▒▒▒▒▒▒▒▒▒░░░▒▒░░▒▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓░░  ▕
        ▏  ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▒░▒▒░  ░░░░▒▒▒▒▒▒▒▒▒▒▒▒▒▒░░▒▒▒▒▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓  ▕
        ▏  ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▒░▒▒░  ░░░▒▒▒▓▓▒▓███▓▓▒▒▒░░▒▒▒▒▒▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓  ▕
        ▏  ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓░▒▒▒░  ░░░▒▒▓█▓▒▓███▓▒▒▒▒░▒▒▒▓▒▒▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓  ▕
        ▏  ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▒▒░▒▒░  ░░▒▒▒▓▓▓▒▒██▓▒▒▒▒▒▒░▓▓▓▒▒▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓  ▕
        ▏  ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▒▒ ░░░░         ░▒░       ░░░▒▒▒░░▒▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓  ▕
        ▏  ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓   ░    ░      ▓▒     ░   ░░░  ░▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓  ▕
        ▏  ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▒░       ░  ░░  ▒░░░   ░▒░░░░▒░▒ ▒▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓  ▕
        ▏  ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓░░    ▒░▒░░░░ ░▓▒▒░▒▒▒▒░▓▒░▒░░▒░▒▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓  ▕
        ▏  ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓     ░░░▒▒░░ ░▓▓▒▒░▓▓▓▒▒░░▒ ░░▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓  ▕
        ▏  ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▒  ░░  ░▒░░  ░▒▒░░▒░▒▓▒░░▒▒░░▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓  ▕
        ▏  ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓░░  ░▒░░░░░   ░ ░ ░░▒░▒▓▒░▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓  ▕
        ▏  ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓░░░░░       ░░░   ░▒▒▓▓▒▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓  ▕
        ▏  ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓  ░▒▒▓░░░░░░▒▒▒▒▓▒▓▒▒▒ ░▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓  ▕
        ▏  ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓░   ░▒▒▒░░▓▒▒▓▓▓▓██▒▒░   ░▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓  ▕
        ▏  ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓       ░▒▓▒▒▓▓▓▓▓▓▒▒░▒      ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓  ▕
        ▏  ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▒░                    ░▒▒▒▒         ░▒▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓  ▕
        ▏  ▓▓▓▓▓▓▓▓▓▓▓▓▒░                ░░  ░ ░▒▒▒▒▓▒ ▒              ▒▓▓▓▓▓▓▓▓▓▓▓▓  ▕
        ▏  ▓▓▓▓▓▓▓▓▒                   ░▒░░▒▒▒▒░░▒▒▒░▒░                   ▒▓▓▓▓▓▓▓▓  ▕
        ▏  ▓▓▓▓▓▓▓                        ░▒█▒▒▒░░ ▒▒▒                      ▒▓▓▓▓▓▓  ▕
        ▏  ▓▓▓▓▓▒   ░░                     ▒▓▓▓▒░ ░░▓                   ░    ▒▓▓▓▓▓  ▕
        ▏  ▓▓▓▓▒                            ░ ░  ░                            ▒▓▓▓▓  ▕
        ▏  ▓▓▓▓       ▒▒▒░░▓▒▒▒▒░░▒▒▓▒▒░░   ░▒░▓▒   ░░▒▒▒▒▒▒▒▒▓▓▒▒▒░▒▓▒░       ▓▓▓▓  ▕
        ▏  ▓▓▓░     ▒▒▒▒▒                    ▒▓░                     ░▓▒▒▒     ░▓▓▓  ▕
        ▏  ▓▓▓▒▓▒░░ ░▒░                                                ░▒░ ▒░░░▒▓▓▓  ▕
        ▏  ▓▓░ ░░▒▒░                                                     ░░░    ▒▓▓  ▕
        ▏  ▓▒                                                                    ▒▓  ▕
        ▏  ▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔  ▕
        ▏                                                                            ▕
        ▏                                     [italic white]Ahmed Al-Farsi, Synthetic Patient #1[/italic white]   ▕
        ▏                                                                            ▕                                                                              
        ▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔                                                                              
    
                    [blue]© Alex Goodell / Simon Chu / AIM Lab
                      [bold]GRANOLA AI[/bold][/blue]
    '''
    rich.print(logo)


def initialize():
    logging_file_path = configure_logging()
    clear()
    logo()
    start_log_task("Loading utilities")
    end_log_task()

    log_mini_task("Logging configured at: " + logging_file_path)
    log_mini_task("Utilities loaded")

if __name__ == "__main__":
    print("hello world")
