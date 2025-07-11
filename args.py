from argparse import ArgumentParser


def parse_args():
    parser = ArgumentParser()
    parser.add_argument("--auth-url", type=str, required=True)
    parser.add_argument("--base-url", type=str, required=True)
    parser.add_argument("--config-path", type=str, default="config.json")
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("--host", type=str, default="0.0.0.0")
    parser.add_argument("--timeout", type=int, default=300)
    
    return parser.parse_args()