import os
from dotenv import dotenv_values

def load_env(path=os.path.join(__file__, *[os.pardir]*2)):
    config = {}
    env_path = os.path.join(path, ".env")
    env_local_path = os.path.join(path, ".env.local")
    if os.path.isfile(env_path):
        config = {
            **dotenv_values(env_path)
        }
    if os.path.isfile(env_local_path):
        config = {
            **config,
            **dotenv_values(env_local_path)
        }
    return config

if __name__ == "__main__":
    print(load_env())