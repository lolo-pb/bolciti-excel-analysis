import sys
import processor as p


def main():
    if len(sys.argv) == 1:
        p.run_processor()
    elif sys.argv[1] == "a":
        print("other")
    else:
        print("Unknown option.")


if __name__ == "__main__":
    main()
