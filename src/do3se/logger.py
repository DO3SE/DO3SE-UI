from pathlib import Path
from datetime import datetime
import subprocess
from typing import List


class Logger:
    def __init__(
        self,
        log_level: int = 0,
        log_to_file: Path = None,
        use_timestamp=True,
        write_mode='a',
        set_as_default: bool = False,
        flush_per_log: bool = False,
    ):
        self.log_level = log_level
        self.log_to_file = log_to_file
        self.use_timestamp = use_timestamp
        self.flush_per_log = flush_per_log
        self.history = []
        self.offset = 0 if not use_timestamp else len(
            str(datetime.now().strftime("%d/%m/%Y %H:%M:%S")) + '\t')
        if log_to_file:
            try:
                f = open(log_to_file, write_mode)
            except FileNotFoundError:
                f = open(log_to_file, 'w')
            t = str(datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
            f.write(f'\n=========== {t} =========\n')
            self.log_file = f

        if set_as_default:
            defaultLogger.__dict__.update(self.__dict__)

    def log(self, *args, **kwargs):
        verbose = kwargs.pop('verbose', False)
        args_to_print = [str(arg).replace('\n', '\n' + self.offset * ' ') for arg in args]
        if self.log_level == -1:
            return
        if verbose and self.log_level < 2:
            return
        if self.log_to_file and self.log_file.closed:
            self.open()
        if self.log_level and self.log_to_file:
            t = str(datetime.now().strftime("%d/%m/%Y %H:%M:%S")) + \
                '\t' if self.use_timestamp else ''
            self.log_file.writelines(t + ', '.join(args_to_print) + '\n')
        if self.log_level and not self.log_to_file:
            t = str(datetime.now().strftime("%d/%m/%Y %H:%M:%S")) + \
                '\t' if self.use_timestamp else ''
            print(t + ', '.join(args_to_print) + '\n')
        if self.flush_per_log and self.log_to_file and self.log_level >= 2:
            # If running verbose we save the file after each log.
            self.flush()
        if self.log_level >= 2:
            t = str(datetime.now().strftime("%d/%m/%Y %H:%M:%S")) + \
                '\t' if self.use_timestamp else ''
            self.history.append(t + ', '.join(args_to_print) + '\n')

    def __call__(self, *args, **kwargs):
        return self.log(*args, **kwargs)

    def flush(self):
        if self.log_to_file:
            self.log_file.flush()

    def close(self):
        if self.log_to_file:
            self.log_file.close()

    def open(self):
        self.log_file = open(self.log_to_file, 'a')


def get_git_revision_hash() -> str:
    """Get the current git commit hash. Only works if running from cloned pyDO3SE."""
    try:
        repr_name = subprocess.check_output(['basename', '\"git rev-parse --show-toplevel\"'])
        if repr_name == 'pyDO3SE':
            return subprocess.check_output(['git', 'rev-parse', 'HEAD']).decode('ascii').strip()
        else:
            return ''
    except:
        return ''


def generate_run_notes(
    runnotes: str = None,
    time_taken: str = None,
    time_taken_setup: str = None,
    config_version: str = None,
    model_version: str = None,
    errors: List[str] = [],
) -> List[str]:
    git_commit = get_git_revision_hash()
    return [
        str(runnotes),
        f"Model took:\t {time_taken}",
        f"Setup took:\t {time_taken_setup}",
        f"Using model version:\t {model_version}",
        f"Using git commit:\t {git_commit}",
        f"Using config version:\t {config_version}",
        f"Date:\t {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}",
        *['Errors: ', *[f'{e}' for e in errors]],
    ]


defaultLogger = Logger()

def wrap_log(message, fn, id="MISSING ID", logger=print):
    """Calls a function and logs any a message and any errors that occur.

    Parameters
    ----------
    message : _type_
        _description_
    fn : function
        _description_
    id : str, optional
        _description_, by default "MISSING ID"
    """
    def _inner(*args, **kwargs):
        logger(id, ':\t', message)
        try:
            return fn(*args, **kwargs)
        except Exception as e:
            logger(f"Failed running function id: {id}")
            raise e
    return _inner
