from dotfile_manager.tool_config import TOOL_CONFIG


def main():
    print(TOOL_CONFIG.model_dump())


if __name__ == "__main__":
    main()
