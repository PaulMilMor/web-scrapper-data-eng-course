import yaml


__config = None


def config():
    """
    > If the global variable `__config` is not set, then open the file `config.yaml` and load the
    contents into the global variable `__config`
    :return: The config.yaml file is being returned.
    """
    global __config
    if not __config:
        with open('config.yaml', mode='r') as f:
            __config = yaml.safe_load(f)
        
    return __config
